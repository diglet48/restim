# Coyote hardware timing and derived limits
# Pulse duration limits in milliseconds
MIN_PULSE_DURATION_MS = 5
MAX_PULSE_DURATION_MS = 240

# Derived hardware frequency limits (Hz)
HARDWARE_MAX_FREQ_HZ = 1000.0 / MIN_PULSE_DURATION_MS  # ~200 Hz
HARDWARE_MIN_FREQ_HZ = 1000.0 / MAX_PULSE_DURATION_MS  # ~4.17 Hz

# Packet and queue behavior
PULSES_PER_PACKET = 4
QUEUE_HORIZON_S = 0.75
PACKET_MARGIN = 0.8  # request next packet when ~80% of current one has played

# Pulse generation behavior
TEXTURE_MIN_HZ = 0.5
TEXTURE_MAX_HZ = 5.0
TEXTURE_MAX_DEPTH_FRACTION = 0.5
JITTER_CLAMP_FRACTION = 0.5
RANDOMIZATION_LIMIT_FRACTION = 0.1  # limit randomization to 10% of setting
RESIDUAL_BOUND = 0.49  # clamp fractional residual for rounding fairness
DEFAULT_MAX_CHANGE_PER_PULSE = 3.0  # percentage points per pulse if setting unavailable

# BLE / Protocol constants
LOG_PREFIX = "[Coyote]"
BATTERY_SERVICE_UUID = "0000180A-0000-1000-8000-00805f9b34fb"
MAIN_SERVICE_UUID = "0000180C-0000-1000-8000-00805f9b34fb"
WRITE_CHAR_UUID = "0000150A-0000-1000-8000-00805f9b34fb"
NOTIFY_CHAR_UUID = "0000150B-0000-1000-8000-00805f9b34fb"
BATTERY_CHAR_UUID = "00001500-0000-1000-8000-00805f9b34fb"

CMD_B0 = 0xB0
CMD_POWER_UPDATE = 0xB1
CMD_ACK = 0x51
CMD_ACTIVE_POWER = 0x53

INTERP_ABSOLUTE_SET = 0b11
INTERP_NO_CHANGE = 0b00
SEQUENCE_MODULO = 16  # 4-bit sequence number wraps at 16
B0_NO_PULSES_PAD_BYTES = 16

# Connection behavior
SCAN_RETRY_SECONDS = 5
