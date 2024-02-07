from dataclasses import dataclass
from enum import Enum
from qt_ui import settings


class DeviceType(Enum):
    NONE = 0
    THREE_PHASE = 1
    FOUR_PHASE = 2
    FIVE_PHASE = 3
    # MODIFY_EXISTING_THREEPHASE_AUDIO = 4


class WaveformType(Enum):
    CONTINUOUS = 1
    PULSE_BASED = 2


@dataclass
class DeviceConfiguration:
    device_type: DeviceType
    waveform_type: WaveformType
    min_frequency: float
    max_frequency: float

    def save(self):
        settings.device_config_device_type.set(self.device_type.value)
        settings.device_config_waveform_type.set(self.waveform_type.value)
        settings.device_config_min_freq.set(self.min_frequency)
        settings.device_config_max_freq.set(self.max_frequency)

    @staticmethod
    def from_settings():
        return DeviceConfiguration(
            DeviceType(settings.device_config_device_type.get()),
            WaveformType(settings.device_config_waveform_type.get()),
            settings.device_config_min_freq.get(),
            settings.device_config_max_freq.get(),
        )