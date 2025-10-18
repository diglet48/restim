import asyncio
from dataclasses import dataclass
import logging
from typing import Optional, Callable
import time
import threading
import numpy as np

from bleak import BleakClient, BleakScanner
from device.output_device import OutputDevice
#from stim_math.audio_gen.coyote import CoyoteThreePhaseAlgorithm #blegh, circular import
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger('restim.coyote')

# Coyote BLE UUIDs
BATTERY_SERVICE_UUID = "0000180A-0000-1000-8000-00805f9b34fb"
MAIN_SERVICE_UUID = "0000180C-0000-1000-8000-00805f9b34fb"
WRITE_CHAR_UUID = "0000150A-0000-1000-8000-00805f9b34fb"
NOTIFY_CHAR_UUID = "0000150B-0000-1000-8000-00805f9b34fb"
BATTERY_CHAR_UUID = "00001500-0000-1000-8000-00805f9b34fb"

class ConnectionStage:
    DISCONNECTED = "Disconnected"
    SCANNING = "Scanning for device..."
    CONNECTING = "Connecting..."
    SERVICE_DISCOVERY = "Discovering services..."
    BATTERY_SUBSCRIBE = "Setting up battery notifications..."
    STATUS_SUBSCRIBE = "Setting up status notifications..."
    SYNC_PARAMETERS = "Syncing parameters..."
    CONNECTED = "Connected"

@dataclass
class CoyoteParams:
    """
    Represents configurable parameters for the Coyote device
    channel_a_limit: 0-200 power limit for channel A
    channel_b_limit: 0-200 power limit for channel B
    channel_a_freq_balance: 0-255 frequency balance for channel A
    channel_b_freq_balance: 0-255 frequency balance for channel B
    channel_a_intensity_balance: 0-255 intensity balance for channel A
    channel_b_intensity_balance: 0-255 intensity balance for channel B
    """
    channel_a_limit: int
    channel_b_limit: int
    channel_a_freq_balance: int
    channel_b_freq_balance: int
    channel_a_intensity_balance: int
    channel_b_intensity_balance: int

@dataclass
class CoyotePulse:
    frequency: int # 0-150 Hz
    intensity: int   # 0-100
    duration: int   # 10-240 (converted from Hz frequency)

@dataclass
class CoyotePulses:
    channel_a: list[CoyotePulse]  # Exactly 4 pulses
    channel_b: list[CoyotePulse]  # Exactly 4 pulses

    def duration() -> int:
        return 0

@dataclass
class CoyoteStrengths:
    """Represents channel strength (volume) settings"""
    channel_a: int  # 0-100
    channel_b: int  # 0-100

class CoyoteDevice(OutputDevice, QObject):
    parameters: CoyoteParams = None
    connection_status_changed = Signal(bool, str)  # Connected, Stage
    battery_level_changed = Signal(int)
    parameters_changed = Signal()
    power_levels_changed = Signal(CoyoteStrengths)
    pulse_sent = Signal(CoyotePulses)
    envelope_updated = Signal(str, np.ndarray, float)  # channel_id, envelope_data, envelope_period

    def __init__(self, device_name: str):
        OutputDevice.__init__(self)
        QObject.__init__(self)
        self.device_name = device_name
        self.client: Optional[BleakClient] = None
        self.algorithm: Optional[any] = None
        self.running = False
        self.connection_stage = ConnectionStage.DISCONNECTED
        self.strengths = CoyoteStrengths(channel_a=0, channel_b=0)
        self.battery_level = 100
        self.parameters = None
        self._event_loop = None
        self.sequence_number = 1
        
        # Start connection process
        self._start_connection_loop()

    def _start_connection_loop(self):
        """Start the connection process in a separate thread"""
        loop = asyncio.new_event_loop()
        self._event_loop = loop
        asyncio.set_event_loop(loop)
        
        def run_loop():
            logger.info("Starting asyncio loop thread")
            loop.run_until_complete(self._connection_loop())
            loop.run_forever()
            
        threading.Thread(target=run_loop, daemon=True).start()

    async def _connection_loop(self):
        """Main connection loop that runs the state machine"""
        logger.info("Starting connection loop")
        prev_stage = self.connection_stage
        
        while True:
            try:
                # Check if client is still connected
                if (self.connection_stage == ConnectionStage.CONNECTED and 
                    (not self.client or not self.client.is_connected)):
                    logger.warning("Device disconnected unexpectedly")
                    await self.disconnect()
                    continue

                if self.connection_stage == ConnectionStage.DISCONNECTED:
                    logger.info("Starting connection process")
                    self.connection_stage = ConnectionStage.SCANNING
                    
                elif self.connection_stage == ConnectionStage.SCANNING:
                    if await self._scan_for_device():
                        logger.info("Device found, connecting...")
                        self.connection_stage = ConnectionStage.CONNECTING
                    else:
                        logger.info("Device not found, retrying in 5 seconds...")
                        await asyncio.sleep(5)
                        
                elif self.connection_stage == ConnectionStage.CONNECTING:
                    if await self.client.connect():
                        logger.info("Connected, discovering services...")
                        self.connection_stage = ConnectionStage.SERVICE_DISCOVERY
                    else:
                        logger.error("Connection failed")
                        await self.disconnect()
                        
                elif self.connection_stage == ConnectionStage.SERVICE_DISCOVERY:
                    if await self.client.get_services():
                        logger.info("Services discovered, subscribing to battery...")
                        self.connection_stage = ConnectionStage.BATTERY_SUBSCRIBE
                    else:
                        logger.error("Service discovery failed")
                        await self.disconnect()
                        
                elif self.connection_stage == ConnectionStage.BATTERY_SUBSCRIBE:
                    if await self._subscribe_to_notifications(BATTERY_CHAR_UUID):
                        logger.info("Battery subscribed, subscribing to status...")
                        self.connection_stage = ConnectionStage.STATUS_SUBSCRIBE
                    else:
                        logger.error("Battery subscription failed")
                        await self.disconnect()
                        
                elif self.connection_stage == ConnectionStage.STATUS_SUBSCRIBE:
                    if await self._subscribe_to_notifications(NOTIFY_CHAR_UUID):
                        logger.info("Status subscribed, syncing parameters...")
                        self.connection_stage = ConnectionStage.SYNC_PARAMETERS
                    else:
                        logger.error("Status subscription failed")
                        await self.disconnect()
                        
                elif self.connection_stage == ConnectionStage.SYNC_PARAMETERS:
                    if await self._send_parameters():
                        logger.info("Parameters synced, connection complete")
                        # TODO: wait for ACK so we know device is ready
                        self.connection_stage = ConnectionStage.CONNECTED
                    else:
                        logger.error("Parameter sync failed")
                        await self.disconnect()
                        
                elif self.connection_stage == ConnectionStage.CONNECTED:
                    # Just maintain the connection
                    await asyncio.sleep(1)
                    
                # Emit signal when connection status changes
                if prev_stage != self.connection_stage:
                    is_connected = self.connection_stage == ConnectionStage.CONNECTED
                    self.connection_status_changed.emit(is_connected, self.connection_stage)
                    prev_stage = self.connection_stage
                
            except Exception as e:
                logger.error(f"Connection loop error: {e}")
                # raise e
                await self.disconnect()
                
            # Small delay between iterations
            await asyncio.sleep(0.1)

    def start_updates(self, algorithm: Optional[any]):
        logger.info("start_updates called")
        self.algorithm = algorithm
        self.running = True

        future = None
        if self._event_loop:
            logger.info("scheduling update_loop in event loop")
            future = asyncio.run_coroutine_threadsafe(self.update_loop(), self._event_loop)
        else:
            logger.error("No event loop present!")

        if future:
            logger.info("Future scheduled")
        else:
            logger.warning("Update loop not scheduled")

    def stop_updates(self):
        """Stop the update loop but maintain connection"""
        logger.info("Stopping updates")
        self.running = False
        self.algorithm = None
        
    async def _handle_battery_notification(self, sender, data: bytearray):
        """Handle battery level notifications"""
        battery_level = data[0]

        logger.info(f"Battery level notification received: {battery_level}%")
        
        self.battery_level = battery_level
        self.battery_level_changed.emit(battery_level)

    async def _handle_status_notification(self, sender, data: bytearray):
        """Handle incoming status notifications from the device."""

        if not data:
            logger.warning("Received empty status notification")
            return

        # if len(data) != 4:
        #     logger.warning(f"Unexpected notification length: {len(data)} - {list(data)}")
        #     return

        command_id = data[0]
        sequence_number = data[1]
        power_a = data[2]
        power_b = data[3]

        if command_id == 0xB1:
            logger.debug(f"Power level update (seq={sequence_number}) - Channel A: {power_a}, Channel B: {power_b}")
            self.strengths.channel_a = power_a
            self.strengths.channel_b = power_b
            self.power_levels_changed.emit(self.strengths)

        elif command_id == 0x51:
            logger.debug(f"Command acknowledged (seq={sequence_number})")
        
        elif command_id == 0x53:
            if len(data) < 4:
                logger.warning(f"Malformed active power notification: {list(data)}")
                return

            power_a = data[2]
            power_b = data[3]

            logger.debug(f"Active power update - Channel A: {power_a}, Channel B: {power_b}")

            # self.strengths.channel_a = power_a
            # self.strengths.channel_b = power_b
            # self.power_levels_changed.emit(self.strengths)

            # if len(data) > 4:
            #     extra = data[4:]
            #     logger.debug(f"Extra fields in 0x53 notification (undocumented): {list(extra)}")

        else:
            logger.warning(f"Unknown notification type: 0x{command_id:02X} (seq={sequence_number})")
            logger.debug(f"Raw notification: {list(data)}")

    async def _send_parameters(self):
        """Send device parameters"""
        logger.info(
            f"Syncing parameters - "
            f"Limits: A={self.parameters.channel_a_limit}, B={self.parameters.channel_b_limit}, "
            f"Freq Balance: A={self.parameters.channel_a_freq_balance}, B={self.parameters.channel_b_freq_balance}, "
            f"Intensity Balance: A={self.parameters.channel_a_intensity_balance}, B={self.parameters.channel_b_intensity_balance}"
        )

        command = bytes([
            0xBF, # Does this command produce an ACK? Only if the seq nibble is > 0
            self.parameters.channel_a_limit,
            self.parameters.channel_b_limit,
            self.parameters.channel_a_freq_balance,
            self.parameters.channel_b_freq_balance,
            self.parameters.channel_a_intensity_balance,
            self.parameters.channel_b_intensity_balance
        ])
        
        try:
            await self.client.write_gatt_char(WRITE_CHAR_UUID, command)
            return True
        except Exception as e:
            logger.error(f"Failed to sync parameters: {str(e)}")
            return False

    async def _subscribe_to_notifications(self, char_uuid: str) -> bool:
        """Subscribe to notifications for a characteristic"""
        try:
            await self.client.start_notify(char_uuid, 
                self._handle_battery_notification if char_uuid == BATTERY_CHAR_UUID 
                else self._handle_status_notification)
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to {char_uuid}: {e}")
            return False

    async def _scan_for_device(self):
        """Scan for Coyote device"""
        try:
            logger.info(f"Scanning for device: {self.device_name}")
            device = await BleakScanner.find_device_by_name(self.device_name)
            if device:
                logger.info(f"Found device: {device.name} ({device.address})")
                self.client = BleakClient(device)
                self.connection_stage = ConnectionStage.CONNECTING
                return True
            else:
                logger.warning(f"Device not found: {self.device_name}")
                await self.disconnect()
                return False
        except Exception as e:
            logger.error(f"Scan error: {str(e)}")
            await self.disconnect()
            return False

    async def send_command(self, 
                            strengths: Optional[CoyoteStrengths] = None,
                            pulses: Optional[CoyotePulses] = None):
        """
        Send strength update and/or pulse pattern command to device.

        Args:
            strengths: Optional strength update for channels A and B
            pulses: Optional pulse patterns for channels A and B
        """

        if pulses:
            self.pulse_sent.emit(pulses)
        
        if not self.client or not self.client.is_connected:
            # logger.warning("Attempted to send command while disconnected")

            # Optimistic update for offline testing
            if strengths:
                self.strengths.channel_a = strengths.channel_a
                self.strengths.channel_b = strengths.channel_b

            return

        if not strengths and not pulses:
            logger.warning("send_command called with no data")
            return

        # Determine strength interpretation (default absolute set if new strength provided)
        if strengths:
            interp_a = 0b11  # Absolute set for Channel A
            interp_b = 0b11  # Absolute set for Channel B
        else:
            interp_a = 0b00  # No change
            interp_b = 0b00  # No change

        # Pack sequence number + interpretation into 1 byte (upper 4 = seq, lower 4 = interp)
        request_ack = not pulses
        control_byte = ((self.sequence_number if request_ack else 0) << 4) | (interp_a << 2) | interp_b

        # Build base command (B0 packet structure)
        command = bytearray([
            0xB0,                     # Command ID
            control_byte,              # Combined seq + interpretation
            strengths.channel_a if strengths else 0,
            strengths.channel_b if strengths else 0,
        ])

        # Append pulse data if provided (waveform duration (aka frequency) + intensity)
        if pulses:
            command.extend([a.duration for a in pulses.channel_a])
            command.extend([a.intensity for a in pulses.channel_a])
            command.extend([b.duration for b in pulses.channel_b])
            command.extend([b.intensity for b in pulses.channel_b])
        else:
            command.extend([0] * 16)  # No pulses = zero padding

        # Log what we're sending
        logger.info(f"Sending command (seq={self.sequence_number}): ")
                    # f"Channel A = {strengths.channel_a if strengths else self.strengths.channel_a}, "
                    # f"Channel B = {strengths.channel_b if strengths else 'N/A'}")

        if pulses:
            pulses_a = "\n".join([f"  Pulse {i+1}: Freq={a.frequency} Hz, Intensity={a.intensity}" for i, a in enumerate(pulses.channel_a)])
            pulses_b = "\n".join([f"  Pulse {i+1}: Freq={b.frequency} Hz, Intensity={b.intensity}" for i, b in enumerate(pulses.channel_b)])
            logger.debug(f"Channel A ({self.strengths.channel_a}):\n{pulses_a}\nChannel B ({self.strengths.channel_b}):\n{pulses_b}")

        # Send the final command
        try:
            await self.client.write_gatt_char(WRITE_CHAR_UUID, command)
            self.sequence_number = (self.sequence_number + 1) % 16  # Wrap seq at 4 bits (0-15)
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
    
    async def disconnect(self):
        """Disconnect from device"""
        logger.info("Disconnecting from Coyote device")

        if self.client:
            self.running = False

            # Send zero pulses to turn off outputs
            zero_pulses = CoyotePulses(
                channel_a=[CoyotePulse(frequency=0, intensity=0, duration=0)] * 4,
                channel_b=[CoyotePulse(frequency=0, intensity=0, duration=0)] * 4
            )
            await self.send_command(pulses=zero_pulses)
            await self.client.disconnect()
        self.client = None
        self.connection_stage = ConnectionStage.DISCONNECTED

    async def update_loop(self):
        logger.info(f"Starting update loop, running={self.running}, algorithm={self.algorithm}")
    
        try:
            logger.info(f"Update loop started, running={self.running}")

            while self.running:
                try:
                    if not self.algorithm:
                        logger.debug("Algorithm not yet set")
                        await asyncio.sleep(0.1)
                        continue

                    current_time = time.time()
                    # Only log when a packet is actually generated and sent
                    if current_time >= self.algorithm.next_update_time:
                        pulses = self.algorithm.generate_packet(current_time)
                        if pulses is not None:
                            await self.send_command(pulses=pulses)
                        sleep_time = max(0.001, self.algorithm.next_update_time - time.time())
                    else:
                        sleep_time = 0.01

                    await asyncio.sleep(sleep_time)

                except Exception as inner_e:
                    logger.exception(f"Exception inside update loop iteration: {inner_e}")
                    await asyncio.sleep(0.1)  # prevent tight-crash-loop

        except Exception as outer_e:
            logger.exception(f"Fatal exception in update_loop: {outer_e}")

        finally:
            logger.info("Update loop stopped")
    
    def is_connected_and_running(self) -> bool:
        return (self.connection_stage == ConnectionStage.CONNECTED and 
                self.client and self.client.is_connected)
