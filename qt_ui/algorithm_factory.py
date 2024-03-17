from __future__ import annotations  # multiple return values
import numpy as np

from qt_ui.device_wizard.enums import DeviceConfiguration, DeviceType, WaveformType
from stim_math.audio_gen.base_classes import AudioGenerationAlgorithm
from stim_math.audio_gen.pulse_based import DefaultThreePhasePulseBasedAlgorithm
from stim_math.audio_gen.continuous import ThreePhaseAlgorithm, FourPhaseAlgorithm, FivePhaseAlgorithm
from stim_math.audio_gen.params import *

from qt_ui.models.funscript_kit import FunscriptKitModel
from qt_ui.models.script_mapping import ScriptMappingModel
from qt_ui.device_wizard.axes import AxisEnum
from stim_math.axis import create_precomputed_axis, AbstractTimestampMapper, create_constant_axis, AbstractMediaSync


class AlgorithmFactory:
    def __init__(self, mainwindow,
                 kit: FunscriptKitModel,
                 script_mapping: ScriptMappingModel,
                 timestamp_mapper: AbstractTimestampMapper,
                 media_sync: AbstractMediaSync,
                 load_funscripts: bool = True,
                 create_for_bake: bool = False,
                 ):
        # TODO: not very nice to reference mainwindow...
        self.mainwindow = mainwindow
        self.kit = kit
        self.script_mapping = script_mapping
        self.timestamp_mapper = timestamp_mapper
        self.media_sync = media_sync
        self.load_funscripts = load_funscripts
        self.create_for_bake = create_for_bake

    def create_algorithm(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        if device.device_type == DeviceType.THREE_PHASE:
            if device.waveform_type == WaveformType.CONTINUOUS:
                return self.create_3phase_continuous(device)
            elif device.waveform_type == WaveformType.PULSE_BASED:
                return self.create_3phase_pulsebased(device)
            else:
                raise RuntimeError('unknown waveform type')
        elif device.device_type == DeviceType.FOUR_PHASE:
            if device.waveform_type == WaveformType.CONTINUOUS:
                return self.create_4phase_continuous(device)
            elif device.waveform_type == WaveformType.PULSE_BASED:
                raise RuntimeError('unsupported device/waveform combination')
            else:
                raise RuntimeError('unknown waveform type')
        elif device.device_type == DeviceType.FIVE_PHASE:
            if device.waveform_type == WaveformType.CONTINUOUS:
                return self.create_5phase_continuous(device)
            elif device.waveform_type == WaveformType.PULSE_BASED:
                raise RuntimeError('unsupported device/waveform combination')
            else:
                raise RuntimeError('unknown waveform type')
        else:
            raise RuntimeError('unknown device type')

    def create_3phase_continuous(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = ThreePhaseAlgorithm(
            self.media_sync,
            ThreephaseContinuousAlgorithmParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    ramp=self.get_axis_volume_ramp(),
                    inactivity=self.get_axis_volume_inactivity(),
                ),
                carrier_frequency=self.get_axis_carrier_frequency(device)
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def create_4phase_continuous(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = FourPhaseAlgorithm(
            self.media_sync,
            FivephaseContinuousAlgorithmParams(
                position=self.mainwindow.tab_fivephase.position,
                calibrate=self.mainwindow.tab_fivephase.calibration,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    ramp=self.get_axis_volume_ramp(),
                    inactivity=self.get_axis_volume_inactivity(),
                ),
                carrier_frequency=self.get_axis_carrier_frequency(device)
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def create_5phase_continuous(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = FivePhaseAlgorithm(
            self.media_sync,
            FivephaseContinuousAlgorithmParams(
                position=self.mainwindow.tab_fivephase.position,
                calibrate=self.mainwindow.tab_fivephase.calibration,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    ramp=self.get_axis_volume_ramp(),
                    inactivity=self.get_axis_volume_inactivity(),
                ),
                carrier_frequency=self.get_axis_carrier_frequency(device)
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def create_3phase_pulsebased(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = DefaultThreePhasePulseBasedAlgorithm(
            self.media_sync,
            ThreephasePulsebasedAlgorithmParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    ramp=self.get_axis_volume_ramp(),
                    inactivity=self.get_axis_volume_inactivity(),
                ),
                carrier_frequency=self.get_axis_carrier_frequency(device),
                pulse_frequency=self.get_axis_pulse_frequency(),
                pulse_width=self.get_axis_pulse_width(),
                pulse_interval_random=self.get_axis_pulse_interval_random(),
                pulse_rise_time=self.mainwindow.tab_pulse_settings.axis_pulse_rise_time,
                pulse_polarity=self.mainwindow.tab_pulse_settings.axis_pulse_polarity,
                device_emulation_mode=self.mainwindow.tab_pulse_settings.axis_device_emulation_mode,
                pulse_phase_offset_increment=self.mainwindow.tab_pulse_settings.axis_pulse_phase_offset_increment,
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def get_axis_alpha(self):
        return self.get_axis_from_script_mapping(AxisEnum.POSITION_ALPHA) or self.mainwindow.alpha

    def get_axis_beta(self):
        return self.get_axis_from_script_mapping(AxisEnum.POSITION_BETA) or self.mainwindow.beta

    def get_axis_volume_api(self):
        return self.get_axis_from_script_mapping(AxisEnum.VOLUME_API) or self.mainwindow.tab_volume.volume.api

    def get_axis_volume_ramp(self):
        if self.create_for_bake:
            return create_constant_axis(1.0)    # ramp does NOT work in bake mode
        return self.mainwindow.tab_volume.volume.ramp

    def get_axis_volume_inactivity(self):
        if self.create_for_bake:
            return create_constant_axis(1.0)    # inactivity does NOT work in bake mode
        return self.mainwindow.tab_volume.volume.inactivity

    def get_axis_carrier_frequency(self, device: DeviceConfiguration):
        if device.waveform_type == WaveformType.CONTINUOUS:
            default = self.mainwindow.tab_carrier.axis_carrier
        elif device.waveform_type == WaveformType.PULSE_BASED:
            default = self.mainwindow.tab_pulse_settings.axis_carrier_frequency
        else:
            raise RuntimeError('unknown waveform type')
        return self.get_axis_from_script_mapping(AxisEnum.CARRIER_FREQUENCY) or default

    def get_axis_pulse_frequency(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_FREQUENCY) or \
               self.mainwindow.tab_pulse_settings.axis_pulse_frequency

    def get_axis_pulse_width(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_WIDTH) or \
               self.mainwindow.tab_pulse_settings.axis_pulse_width

    def get_axis_pulse_interval_random(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_INTERVAL_RANDOM) or \
               self.mainwindow.tab_pulse_settings.axis_pulse_interval_random

    def get_axis_vib1_all(self):
        return VibrationParams(
            enabled=self.get_axis_vib1_enabled(),
            frequency=self.get_axis_vib1_frequency(),
            strength=self.get_axis_vib1_strength(),
            left_right_bias=self.get_axis_vib1_left_right_bias(),
            high_low_bias=self.get_axis_vib1_high_low_bias(),
            random=self.get_axis_vib1_random(),
        )

    def get_axis_vib1_enabled(self):
        is_enabled = \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_FREQUENCY) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_STRENGTH) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_HIGH_LOW_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_RANDOM)
        if is_enabled:
            return create_precomputed_axis([0], [True], self.timestamp_mapper)
        else:
            return self.mainwindow.tab_vibrate.vibration_1.enabled

    def get_axis_vib1_frequency(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_FREQUENCY) or \
               self.mainwindow.tab_vibrate.vibration_1.frequency

    def get_axis_vib1_strength(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_STRENGTH) or \
               self.mainwindow.tab_vibrate.vibration_1.strength

    def get_axis_vib1_left_right_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_1.left_right_bias

    def get_axis_vib1_high_low_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_HIGH_LOW_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_1.high_low_bias

    def get_axis_vib1_random(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_RANDOM) or \
               self.mainwindow.tab_vibrate.vibration_1.random

    def get_axis_vib2_all(self):
        return VibrationParams(
            enabled=self.get_axis_vib2_enabled(),
            frequency=self.get_axis_vib2_frequency(),
            strength=self.get_axis_vib2_strength(),
            left_right_bias=self.get_axis_vib2_left_right_bias(),
            high_low_bias=self.get_axis_vib2_high_low_bias(),
            random=self.get_axis_vib2_random(),
        )

    def get_axis_vib2_enabled(self):
        is_enabled = \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_FREQUENCY) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_STRENGTH) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_HIGH_LOW_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_RANDOM)
        if is_enabled:
            return create_precomputed_axis([0], [True], self.timestamp_mapper)
        else:
            return self.mainwindow.tab_vibrate.vibration_2.enabled

    def get_axis_vib2_frequency(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_FREQUENCY) or \
               self.mainwindow.tab_vibrate.vibration_2.frequency

    def get_axis_vib2_strength(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_STRENGTH) or \
               self.mainwindow.tab_vibrate.vibration_2.strength

    def get_axis_vib2_left_right_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_2.left_right_bias

    def get_axis_vib2_high_low_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_HIGH_LOW_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_2.high_low_bias

    def get_axis_vib2_random(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_RANDOM) or \
               self.mainwindow.tab_vibrate.vibration_2.random

    def get_axis_from_script_mapping(self, axis: AxisEnum) -> AbstractAxis | None:
        if not self.load_funscripts:
            return None

        funscript_item = self.script_mapping.get_config_for_axis(axis)
        if funscript_item:
            limit_min, limit_max = self.kit.limits_for_axis(axis)
            # TODO: not very memory efficient if multiple algorithms reference the same script.
            # but worst-case it only wastes a few MB or so...
            return create_precomputed_axis(funscript_item.script.x,
                                           np.clip(funscript_item.script.y, 0, 1) * (limit_max - limit_min) + limit_min,
                                           self.timestamp_mapper)
        else:
            return None
