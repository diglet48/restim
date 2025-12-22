from dataclasses import dataclass


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
    frequency: int  # Calculated from duration: 1000/duration_ms, range ~4-200 Hz
    intensity: int  # 0-100
    duration: int   # 5-240ms (spec says 10-240, but 5ms works)


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
