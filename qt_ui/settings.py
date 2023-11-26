
from PyQt5.QtCore import QSettings


class Setting:
    def __init__(self, key, default_value, dtype):
        self.key = key
        self.default_value = default_value
        self.dtype = dtype

    def get(self):
        return QSettings().value(self.key, self.default_value, self.dtype)

    def set(self, value):
        QSettings().setValue(self.key, value)


class NonPersistentSetting:
    def __init__(self, default_value):
        self.value = default_value

    def get(self):
        return self.value

    def set(self, value):
        pass


device_type = Setting('global/device_type', 0, int)

pulse_carrier_frequency = Setting('carrier/pulse_carrier_frequency', 700, float)
pulse_frequency = Setting('carrier/pulse_frequency', 50, float)
pulse_width = Setting('carrier/pulse_width', 5, float)
pulse_interval_random = Setting('carrier/pulse_interval_random', 10, float)
pulse_polarity = NonPersistentSetting('random')
pulse_device_emulation_mode = NonPersistentSetting('continuous (best)')
pulse_phase_offset_increment = NonPersistentSetting(0.0)

volume_ramp_time = Setting('volume/inactivity_ramp_time', 3.0, float)
volume_inactivity_threshold = Setting('volume/inactivity_inactive_threshold', 2.0, float)
volume_increment_rate = Setting('volume/increment_rate', 1.0, float)

mk312_carrier = Setting('mk312/carrier_frequency', 700, float)

vibration_1_enabled = Setting('vibration/vibration_1_enabled', False, bool)
vibration_1_frequency = Setting('vibration/vibration_1_frequency', 10, float)
vibration_1_strength = Setting('vibration/vibration_1_strength', 50, float)
vibration_1_left_right_bias = Setting('vibration/vibration_1_left_right_bias', 0.0, float)
vibration_1_high_low_bias = Setting('vibration/vibration_1_high_low_bias', 0.0, float)
vibration_1_random = Setting('vibration/vibration_1_random', 0, float)

vibration_2_enabled = Setting('vibration/vibration_2_enabled', False, bool)
vibration_2_frequency = Setting('vibration/vibration_2_frequency', 2, float)
vibration_2_strength = Setting('vibration/vibration_2_strength', 30, float)
vibration_2_left_right_bias = Setting('vibration/vibration_2_left_right_bias', 80.0, float)
vibration_2_high_low_bias = Setting('vibration/vibration_2_high_low_bias', 10.0, float)
vibration_2_random = Setting('vibration/vibration_2_random', 0, float)
