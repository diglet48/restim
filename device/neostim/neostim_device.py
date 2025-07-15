import logging
import struct
from abc import abstractmethod

import time
import crc
from enum import Enum
import numpy as np
from dataclasses import dataclass


from PySide6.QtCore import QIODevice, QObject
from PySide6.QtSerialPort import QSerialPort


logger = logging.getLogger('restim.neostim')

BAUD_RATE = 115200

FIRMWARE_VERSION = b'v0.59-restim'


class StructureSize(Enum):
    FrameHeader = 8
    MaxPayload = 512
    PacketHeader = 6
    AttributeAction = 6

class FrameType(Enum):
    Non = 0
    Ack = 1
    Nak = 2
    Sync = 3
    Data = 4

class NST(Enum):    # network service type
    Debug = 0
    Datagram = 1

class AttributeId(Enum):
    FirmwareVersion = 2
    Voltages = 3
    ClockMicros = 4
    AllPatternNames = 5
    CurrentPatternName = 6
    IntensityPercent = 7
    PlayPauseStop = 8
    BoxName = 9
    PTDescriptorQueue = 10
    HeartbeatIntervalSecs = 11
    Restim = 12

# Encodings.
class Encoding(Enum):
    UnsignedInt1 = 4
    UnsignedInt2 = 5
    UnsignedInt4 = 6
    UnsignedInt8 = 7
    BooleanFalse = 8
    BooleanTrue = 9
    UTF8_1Len = 12
    Bytes_1Len = 16
    Array = 22
    EndOfContainer = 24

# Request & response types (aka opcodes).
class OPCode(Enum):
    StatusResponse = 1
    ReadRequest = 2
    SubscribeRequest = 3
    SubscribeResponse = 4
    ReportData = 5
    WriteRequest = 6
    WriteResponse = 7
    InvokeRequest = 8
    InvokeResponse = 9

# Status codes.
class StatusCode(Enum):
    Success = 0

class PlayState(Enum):
    Unknown = 0
    Idle = 1
    Paused = 2
    Playing = 3
    Streaming = 4


def crc8_ccit(data):
    return crc.Calculator(crc.Crc8.CCITT).checksum(data)

def crc16_ccit(data):
    return crc.Calculator(crc.Crc16.IBM_3740).checksum(data)


@dataclass
class Burst:
    meta:               np.uint8            # Type, version, flags, etc., for correct interpretation of this descriptor.
    sequence_number:    np.uint8            # For diagnostics. Wraps around to 0 after 255.
    phase:              np.uint8            # Bits 2..1 select 1 of 4 biphasic output stages. Bit 0 is the selected stage's polarity.
    pulse_width_µs:     np.uint8            # The duration of one pulse [µs].
    start_time_us:      np.uint32           # When this burst should begin, relative to the start of the stream.
    electrode_set:      [np.uint8, np.uint8]           # The (max 8) electrodes connected to each of the two output phases.
    nr_of_pulses:       np.uint16           # Length of this burst.
    pace_1_4_ms:        np.uint8            # [0.25 ms] time between the start of consecutive pulses.
    amplitude:          np.uint8            # Voltage, current or power, in units of 1/255 of the set maximum.
    # The following two members [-128..127] are applied after each pulse.
    delta_pulse_width_1_4_µs:   np.int8     # [0.25 µs]. Changes the duration of a pulse.
    delta_pace_µs:              np.int8     # [µs]. Modifies the time between pulses.
    # delta_amplitude   np.int8             # Under consideration.

    def __bytes__(self):
        return struct.pack(
            b'<BBBBIBBHBBBB',
            self.meta,
            self.sequence_number,
            self.phase,
            self.pulse_width_µs,
            self.start_time_us,
            self.electrode_set[0], self.electrode_set[1],
            self.nr_of_pulses,
            self.pace_1_4_ms,
            self.amplitude,
            self.delta_pulse_width_1_4_µs,
            self.delta_pace_µs
        )

    def __len__(self):
        return 16

@dataclass
class RestimPulseParameters:
    a_bd_power: np.uint16       # in 1/1024 of max
    b_ac_power: np.uint16       # in 1/1024 of max
    c_bd_power: np.uint16       # in 1/1024 of max
    d_ac_power: np.uint16       # in 1/1024 of max

    ab_power:   np.uint16       # in 1/1024 of max
    bc_power:   np.uint16       # in 1/1024 of max
    cd_power:   np.uint16       # in 1/1024 of max
    ad_power:   np.uint16       # in 1/1024 of max

    burst_duty_cycle_at_max_power:  np.uint16   # 0 .. 1024
    burst_width_us:                 np.uint16   # 0 .. 1024 µs
    inversion_time_us:              np.uint16   # µs between positive and negative part of the pulse
    triac_switch_time_us:           np.uint16   # µs between 2 pulses with different triac configs

    time_between_pulses_us:    np.uint32

    flags:  np.uint8
    defeat_pulse_randomization: np.uint8


    def __bytes__(self):
        return struct.pack(
            b'<HHHH HHHH HHHH IBBxx',
            self.a_bd_power,
            self.b_ac_power,
            self.c_bd_power,
            self.d_ac_power,
            self.ab_power,
            self.bc_power,
            self.cd_power,
            self.ad_power,
            self.burst_duty_cycle_at_max_power,
            self.burst_width_us,
            self.inversion_time_us,
            self.triac_switch_time_us,
            self.time_between_pulses_us,
            self.flags,
            self.defeat_pulse_randomization)


@dataclass
class AttributeAction:
    trans_id: np.uint16
    request_type: np.uint8  # opcode
    reserved: np.uint8
    attribute_id: np.uint16
    data: bytes = b''

    @staticmethod
    def parse(data):
        return AttributeAction(
            *struct.unpack(b'<HBBH', data[:6]), data[6:]
        )

    def __bytes__(self):
        return struct.pack(b'<HBBH', self.trans_id, self.request_type, self.reserved, self.attribute_id) + bytes(self.data)

    def __len__(self):
        return 6 + len(self.data)


@dataclass()
class Frame:
    meta: np.uint8              # (service_type << 4) | (frame_type << 1);
    seq: np.uint8               # seq << 3
    payload_size: np.uint16 = 0 # in bytes
    byte_4: np.uint8 = 0        # not used?
    crc8: np.uint8 = 0          # crc of first 5 bytes in frame
    crc16: np.uint16 = 0        # crc of payload
    payload: bytes = b''

    @staticmethod
    def init_frame(payload, frame_type: FrameType, service_type: NST, seq):
        return Frame((service_type.value << 4) | (frame_type.value << 1), (seq << 3) & 0xFF, len(payload), 0, 0, 0, payload)


    def fill_crc(self):
        data = struct.pack(b'>BBHB', self.meta, self.seq, self.payload_size, self.byte_4)
        self.crc8 = crc8_ccit(data)

        register = crc.Register(crc.Crc16.IBM_3740)
        data = struct.pack(b'>BBHBB', self.meta, self.seq, self.payload_size, self.byte_4, self.crc8)
        register.update(data)
        register.update(bytes(self.payload))
        self.crc16 = register.digest()

    def __bytes__(self):
        return struct.pack(
            b'>BBHBBH',
            self.meta,
            self.seq,
            self.payload_size,
            self.byte_4,
            self.crc8,
            self.crc16
        ) + bytes(self.payload)


@dataclass
class PacketHeader:
    @staticmethod
    def init_header():
        return PacketHeader()

    def __bytes__(self):
        # just null bytes for now...
        return b'\0'*6

    def __len__(self):
        return 6



class NeoStimPTGenerator:
    """
    Base class for signal generation algorithms.
    """
    def __init__(self):
        pass

    @abstractmethod
    def link_device(self, device):
        pass

    @abstractmethod
    def device_connected_and_ready(self):
        pass

    @abstractmethod
    def device_about_to_disconnect(self):
        pass


class NeoStim(QObject):
    def __init__(self):
        super().__init__()

        self.algorithm: NeoStimPTGenerator = None
        self.serial = None
        self.tx_seq_nr = 0
        self.transaction_id = 0
        self.rx_frame = bytearray(b'')
        self.incoming_payload_size = 0

        self.checked_firmware_version = False

    def start(self, com_port, algorithm: NeoStimPTGenerator):  # todo: add algo
        self.tx_seq_nr = 0
        self.transaction_id = 1000
        self.rx_frame = bytearray(b'')
        
        self.algorithm = algorithm
        algorithm.link_device(self)

        self.port = QSerialPort(self)
        self.port.setPortName(com_port)
        self.port.setBaudRate(BAUD_RATE)
        self.port.readyRead.connect(self.new_serial_data)
        self.port.errorOccurred.connect(self.error_occured)
        success = self.port.open(QIODevice.ReadWrite)
        if success:
            self.port.clear()
            logger.info(f'Successfully opened: {self.port.portName()}')
            self.write(bytes(self.make_sync_frame(NST.Debug)))
            self.send_attr_read_request(AttributeId.FirmwareVersion)
            self.send_attr_read_request(AttributeId.BoxName)
            self.send_attr_read_request(AttributeId.Voltages)
            # self.send_attr_read_request(AttributeId.ClockMicros)
            self.send_attr_read_request(AttributeId.PTDescriptorQueue)

            # self.send_attr_subscribe_request(AttributeId.CurrentPatternName)
            self.send_attr_subscribe_request(AttributeId.IntensityPercent)
            self.send_attr_subscribe_request(AttributeId.PlayPauseStop)
            # self.send_attr_subscribe_request(AttributeId.PTDescriptorQueue)

            self.send_attr_read_request(AttributeId.IntensityPercent)

            # disable the heartbeat
            self.send_attr_write_request(AttributeId.HeartbeatIntervalSecs,
                                                struct.pack(b'<BH', Encoding.UnsignedInt2.value, 0))
        else:
            logger.error(f'Unable to open serial port: {self.port.errorString()}')

    def stop(self):
        # re-enable the heartbeat
        self.send_attr_write_request(AttributeId.HeartbeatIntervalSecs,
                                     struct.pack(b'<BH', Encoding.UnsignedInt2.value, 120))
        self.algorithm.device_about_to_disconnect()
        t = time.time() + .100
        while t >= time.time():
            self.port.flush()
            self.port.waitForBytesWritten(10)
        self.port.close()

    def is_connected_and_running(self) -> bool:
        return self.port and self.port.isOpen()

    def make_ack_frame(self, service_type: NST, ack) -> Frame:
        packet = Frame.init_frame(b'', FrameType.Ack, service_type, 0)
        packet.meta |= 1
        packet.seq |= ack & 0x07
        packet.fill_crc()
        return packet

    def make_sync_frame(self, service_type: NST):
        packet = Frame.init_frame(b'', FrameType.Sync, service_type, self.tx_seq_nr)
        self.tx_seq_nr += 1
        packet.fill_crc()
        return packet

    def make_command_frame(self, cmnd_str):
        """
        const enc_cmnd = new TextEncoder().encode(cmnd_str);
        const frame = initFrame(enc_cmnd.length, FRAME_TYPE_DATA, NST_DEBUG, tx_seq_nr++);
        frame.set(enc_cmnd, FRAME_HEADER_SIZE);
        return crcFrame(frame);
        """
        pass

    def make_request_packet_frame(self, trans_id, request_type: OPCode, attribute_id: AttributeId, data=b''):
        header = PacketHeader.init_header()
        aa = AttributeAction(trans_id, request_type.value, 0, attribute_id.value, data)
        packet = Frame.init_frame(bytes(header) + bytes(aa), FrameType.Data, NST.Datagram, self.tx_seq_nr)
        self.tx_seq_nr += 1
        packet.fill_crc()
        return packet

    def send_attr_read_request(self, attribute_id: AttributeId):
        packet = self.make_request_packet_frame(self.transaction_id, OPCode.ReadRequest, attribute_id, b'')
        self.transaction_id = (self.transaction_id + 1) & 0xFFFF
        self.write(bytes(packet))

    def send_attr_write_request(self, attribute_id: AttributeId, data):
        packet = self.make_request_packet_frame(self.transaction_id, OPCode.WriteRequest, attribute_id, data)
        self.transaction_id = (self.transaction_id + 1) & 0xFFFF
        self.write(bytes(packet))

    def send_attr_subscribe_request(self, attribute_id: AttributeId):
        packet = self.make_request_packet_frame(self.transaction_id, OPCode.SubscribeRequest, attribute_id, b'')
        self.transaction_id = (self.transaction_id + 1) & 0xFFFF
        self.write(bytes(packet))

    def send_attr_invoke_request(self, attribute_id: AttributeId, data):
        # print('invoke')
        packet = self.make_request_packet_frame(self.transaction_id, OPCode.InvokeRequest, attribute_id, data)
        self.transaction_id = (self.transaction_id + 1) & 0xFFFF
        self.write(bytes(packet))

    def queue_pt_descriptor(self, pt: Burst):
        # print('queue pt')
        payload = struct.pack(b'BB', Encoding.Bytes_1Len.value, len(pt)) + bytes(pt)
        packet = self.make_request_packet_frame(self.transaction_id, OPCode.WriteRequest, AttributeId.PTDescriptorQueue, payload)
        self.transaction_id = (self.transaction_id + 1) & 0xFFFF
        self.write(bytes(packet))

    def queue_restim_parameters(self, params: RestimPulseParameters):
        payload = bytes(params)
        payload = struct.pack(b'BB', Encoding.Bytes_1Len.value, len(payload)) + payload
        packet = self.make_request_packet_frame(self.transaction_id, OPCode.WriteRequest,
                                                AttributeId.Restim, payload)
        self.transaction_id = (self.transaction_id + 1) & 0xFFFF
        self.write(bytes(packet))

    def start_queued_pulses(self):
        payload = struct.pack(b'B', Encoding.BooleanTrue.value)
        self.send_attr_invoke_request(AttributeId.PTDescriptorQueue, payload)

    def start_restim(self):
        payload = struct.pack(b'B', Encoding.BooleanTrue.value)
        self.send_attr_invoke_request(AttributeId.Restim, payload)

    def stop_restim(self):
        payload = struct.pack(b'B', Encoding.BooleanFalse.value)
        self.send_attr_invoke_request(AttributeId.Restim, payload)

    def handle_incoming_debug_packet(self, data):
        logger.info(f'debug msg: {data}')

    def handle_incoming_datagram(self, data):
        packet = data[StructureSize.PacketHeader.value:]
        aa = AttributeAction.parse(packet)
        payload = aa.data
        # logger.info(aa)

        if aa.request_type == OPCode.ReportData.value:
            if aa.attribute_id == AttributeId.FirmwareVersion.value:
                if payload[0] == Encoding.UTF8_1Len.value:
                    firmware_version_string = payload[2:]
                    self.handle_read_firmwareversion(firmware_version_string)
                else:
                    logger.error(f'Couldn\'t parse {aa}')
            elif aa.attribute_id == AttributeId.Voltages.value:
                if len(payload) >= 8 and payload[0] == Encoding.Bytes_1Len.value:
                    vbat_mv, vcap_mv, ipri_ma = struct.unpack(b'<HHH', payload[2:8])
                    self.handle_read_voltages(vbat_mv, vcap_mv, ipri_ma)
                else:
                    logger.error(f'Couldn\'t parse {aa}')
            elif aa.attribute_id == AttributeId.ClockMicros.value:
                if len(payload) >= 9 and payload[0] == Encoding.UnsignedInt8.value:
                    micros = struct.unpack(b'<q', payload[1:])
                    self.handle_read_clockmicros(micros)
                else:
                    logger.error(f'Couldn\'t parse {aa}')
            elif aa.attribute_id == AttributeId.AllPatternNames.value:
                pass
            elif aa.attribute_id == AttributeId.CurrentPatternName.value:
                pass
            elif aa.attribute_id == AttributeId.IntensityPercent.value:
                if len(payload) >= 2 and payload[0] == Encoding.UnsignedInt1.value:
                    intensity_percent = struct.unpack(b'B', payload[1:2])[0]
                    self.handle_read_intensity_percent(intensity_percent)
                else:
                    logger.error(f'Couldn\'t parse {aa}')
            elif aa.attribute_id == AttributeId.PlayPauseStop.value:
                if len(payload) >= 2 and payload[0] == Encoding.UnsignedInt1.value:
                    playPauseStop = struct.unpack(b'B', payload[1:2])[0]
                    self.handle_read_play_pause_stop(PlayState(playPauseStop))
                else:
                    logger.error(f'Couldn\'t parse {aa}')
            elif aa.attribute_id == AttributeId.BoxName.value:
                if payload[0] == Encoding.UTF8_1Len.value:
                    box_name = payload[2:]
                    self.handle_read_box_name(box_name)
                else:
                    logger.error(f'Couldn\'t parse {aa}')
            elif aa.attribute_id == AttributeId.PTDescriptorQueue.value:
                if len(payload) >= 6 and payload[0] == Encoding.Bytes_1Len.value:
                    free_queue_bytes = struct.unpack(b'<HH', payload[2:6])
                    logger.info(f'free bytes: {free_queue_bytes}')
                else:
                    logger.info(f'PTDescriptorQueue {aa} / {payload}')
            else:
                logger.info(f'unknown attribute ID {aa.attribute_id}')
        else:
            # print(aa)
            pass

    def handle_read_firmwareversion(self, firmware_version: bytes):
        if firmware_version == FIRMWARE_VERSION:
            if not self.checked_firmware_version:
                self.checked_firmware_version = True
                logger.info(f'found firmware version: {firmware_version.decode("utf-8")}')
                # defer signal generation until compatible firmware version is confirmed.
                self.algorithm.device_connected_and_ready()
        else:
            logger.error(f'Incompatible firmware version. Got "{firmware_version.decode("utf-8")}" expected "{FIRMWARE_VERSION.decode("utf-8")}"')
            self.stop()

    def handle_read_voltages(self, vbat_mv, vcap_mv, ipri_ma):
        logger.info(f'Vbat={vbat_mv} mV, Vcap= {vcap_mv} mV, Ipri= {ipri_ma} mA')

    def handle_read_clockmicros(self, micros: int):
        logger.info('clock micros:', micros)

    def handle_read_intensity_percent(self, intensity: int):
        logger.info(f'intensity: {intensity} / 255')

    def handle_read_box_name(self, box_name):
        logger.info(f'box name: {box_name}')

    def handle_read_play_pause_stop(self, play_pause_stop: PlayState):
        logger.info(f'play pause stop: {play_pause_stop}')

    def assemble_incoming_frame(self, value) -> bytearray | None:
        self.rx_frame.append(value)

        # Collect bytes until we have a complete header.
        if len(self.rx_frame) < StructureSize.FrameHeader.value:
            return None

        # Shift/append the input buffer until it contains a valid header.
        if len(self.rx_frame) == StructureSize.FrameHeader.value:
            if self.rx_frame[5] != crc8_ccit(self.rx_frame[:5]):
                self.rx_frame = self.rx_frame[1:]
                return None
            # Valid header received, start collecting the payload (if any).
            self.incoming_payload_size = struct.unpack('>H', self.rx_frame[2:4])[0]
            if self.incoming_payload_size > StructureSize.MaxPayload.value:
                logger.error(f'Frame payload too big: {self.incoming_payload_size} bytes')
                return None

        if len(self.rx_frame) == (StructureSize.FrameHeader.value + self.incoming_payload_size):
            copy = self.rx_frame
            self.rx_frame = bytearray()
            return copy

        return None

    def new_serial_data(self):
        for value in self.port.readAll():
            frame = self.assemble_incoming_frame(ord(value))
            if frame == None:
                continue

            # print('incoming packet:', frame, self.incoming_payload_size)

            frame_type = FrameType(frame[0] >> 1 & 0x07)
            if frame_type == FrameType.Ack:
                # logger.info(f'Got ACK {frame[1] & 0x07:x}')
                continue

            service_type = NST(frame[0] >> 4 & 0x03)
            if frame_type == FrameType.Data:
                seq = frame[1] >> 3 & 0x07
                self.write(bytes(self.make_ack_frame(service_type, seq)))

            if self.incoming_payload_size == 0:
                continue

            packet = frame[StructureSize.FrameHeader.value:]
            if service_type == NST.Debug:
                self.handle_incoming_debug_packet(packet)
            elif service_type == NST.Datagram:
                self.handle_incoming_datagram(packet)

    def error_occured(self, error):
        if error != 0:
            logger.error(f'serial error: {self.port.errorString()} {error}')
            if self.port.isOpen():
                self.stop()

    def write(self, data):
        # print('sending packet:', len(data), data, [x for x in bytes(data)])
        self.port.write(data)
