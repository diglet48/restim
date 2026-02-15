import time

import numpy as np

from stim_math.audio_gen.base_classes import RemoteGenerationAlgorithm
from stim_math.audio_gen.params import SafetyParamsFOC, FOCStimParams, FourphaseFOCStimParams
from stim_math.audio_gen.various import FourPhaseIntensity
from stim_math.axis import AbstractMediaSync
from device.focstim.constants_pb2 import AxisType
from stim_math import limits


class FOCStimFourphaseAlgorithm(RemoteGenerationAlgorithm):
    def __init__(self, media: AbstractMediaSync, params: FourphaseFOCStimParams, safety_limits: SafetyParamsFOC):
        super().__init__()
        self.media = media
        self.params = params
        self.safety_limits = safety_limits
        self.intensity_params = FourPhaseIntensity(params.position)

        epsilon = 0.0001
        assert safety_limits.waveform_amplitude_amps >= (limits.WaveformAmpltiudeFOC.min - epsilon)
        assert safety_limits.waveform_amplitude_amps <= (limits.WaveformAmpltiudeFOC.max + epsilon)

    # todo: more descriptive name
    def outputs(self):
        return 4

    def parameter_dict(self) -> dict:
        def remap(value, min_value, max_value):
            p = (value - min_value) / (max_value - min_value)
            return np.clip(p, 0, 1)

        t = time.time()

        volume = \
            np.clip(self.params.volume.master.last_value(), 0, 1) * \
            np.clip(self.params.volume.api.interpolate(t), 0, 1) * \
            np.clip(self.params.volume.inactivity.last_value(), 0, 1) * \
            np.clip(self.params.volume.external.last_value(), 0, 1)

        maximum_frequency = np.clip(limits.CarrierFrequencyFOC.max,
                                    self.safety_limits.minimum_carrier_frequency,
                                    self.safety_limits.maximum_carrier_frequency)
        minimum_frequency = np.clip(limits.CarrierFrequencyFOC.min,
                                    self.safety_limits.minimum_carrier_frequency,
                                    self.safety_limits.maximum_carrier_frequency)
        tau = self.params.tau.last_value() * 1e-6

        carrier_frequency = self.params.carrier_frequency.interpolate(t)
        carrier_frequency = np.clip(carrier_frequency, minimum_frequency, maximum_frequency)
        derating = self.frequency_derating_factor(maximum_frequency, carrier_frequency, tau)
        volume *= np.clip(derating, 0, 1)

        a, b, c, d = self.intensity_params.get_position(t)

        if not self.media.is_playing():
            volume *= 0

        return {
            AxisType.AXIS_ELECTRODE_1_POWER: a,
            AxisType.AXIS_ELECTRODE_2_POWER: b,
            AxisType.AXIS_ELECTRODE_3_POWER: c,
            AxisType.AXIS_ELECTRODE_4_POWER: d,
            AxisType.AXIS_WAVEFORM_AMPLITUDE_AMPS: volume * volume * self.safety_limits.waveform_amplitude_amps,
            AxisType.AXIS_CARRIER_FREQUENCY_HZ: carrier_frequency,
            AxisType.AXIS_PULSE_FREQUENCY_HZ: self.params.pulse_frequency.interpolate(t),
            AxisType.AXIS_PULSE_WIDTH_IN_CYCLES: self.params.pulse_width.interpolate(t),
            AxisType.AXIS_PULSE_RISE_TIME_CYCLES: self.params.pulse_rise_time.interpolate(t),
            AxisType.AXIS_PULSE_INTERVAL_RANDOM_PERCENT: self.params.pulse_interval_random.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_CENTER: self.params.calibrate.center.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_A: self.params.calibrate.a.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_B: self.params.calibrate.b.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_C: self.params.calibrate.c.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_D: self.params.calibrate.d.interpolate(t),
        }

    def frequency_derating_factor(self, max_frequency, frequency, tau):
        """
        :param max_frequency:   carrier frequency at which derating = 1 (i.e. no derating)
        :param frequency:       carrier frequency of the pulse
        :param tau:             time constant of the nerves, ~355e-6
        :return:                volume of the pulse, such that it has equal subjective intensity as a pulse at max carrier frequency.
        """
        # this formula follows from Qt = Q0 * (1 + pw/tau)
        return (frequency * tau + 0.5) / (max_frequency * tau + 0.5)
