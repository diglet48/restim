import time

import numpy as np

from stim_math.audio_gen.base_classes import RemoteGenerationAlgorithm
from stim_math.audio_gen.params import SafetyParamsFOC, FOCStimParams, FourphaseFOCStimParams
from stim_math.fourphase_intensity import FourPhaseIntensity
from stim_math.axis import AbstractMediaSync
import stim_math.burst_gap
from device.focstim.constants_pb2 import AxisType
from stim_math import limits
from stim_math.pulse_frequency_calibration import PulseFrequencyCalibration
from stim_math.tau_calibration import TauCalibration


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

        self.sensor_node = None

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
        carrier_calibration = TauCalibration.derating_factor(maximum_frequency, carrier_frequency, tau)
        volume *= np.clip(carrier_calibration, 0, 1)

        pulse_frequency = np.clip(self.params.pulse_frequency.interpolate(t),
                                  limits.PulseFrequency.min, limits.PulseFrequency.max)
        pulse_width = np.clip(self.params.pulse_width.interpolate(t),
                              limits.PulseWidth.min, limits.PulseWidth.max)

        # convert burst freq to pulse freq (if applicable) and limit gap to 5ms
        pulse_width_in_s = np.clip(pulse_width / carrier_frequency, None, limits.PulseDuration.max)
        if self.params.enable_burst_gap.last_value():
            pause_width_in_s = np.clip(1 / pulse_frequency,
                                       limits.InterPulseIntervalDuration.min, limits.InterPulseIntervalDuration.max)
        else:
            pause_width_in_s = np.clip(1 / pulse_frequency - pulse_width_in_s,
                                       limits.InterPulseIntervalDuration.min, limits.InterPulseIntervalDuration.max)
        pulse_frequency = 1 / (pulse_width_in_s + pause_width_in_s)

        if self.params.enable_pulse_frequency_adjustment.last_value():
            pulse_frequency_calibration = PulseFrequencyCalibration.scale(pulse_frequency)
            volume *= np.clip(pulse_frequency_calibration, 0, 1)

        a, b, c, d = self.intensity_params.get_position(t)

        if self.sensor_node:
            params = {'volume': volume, 'e1': a, 'e2': b, 'e3': c, 'e4': d}
            self.sensor_node.process(params)
            # safety: new volume must be less than original
            volume = np.clip(params['volume'], 0, volume)
            a = params['e1']
            b = params['e2']
            c = params['e3']
            d = params['e4']

        if not self.media.is_playing():
            volume *= 0

        return {
            AxisType.AXIS_ELECTRODE_1_POWER: a,
            AxisType.AXIS_ELECTRODE_2_POWER: b,
            AxisType.AXIS_ELECTRODE_3_POWER: c,
            AxisType.AXIS_ELECTRODE_4_POWER: d,
            AxisType.AXIS_WAVEFORM_AMPLITUDE_AMPS: volume * self.safety_limits.waveform_amplitude_amps,
            AxisType.AXIS_CARRIER_FREQUENCY_HZ: carrier_frequency,
            AxisType.AXIS_PULSE_FREQUENCY_HZ: pulse_frequency,
            AxisType.AXIS_PULSE_WIDTH_IN_CYCLES: self.params.pulse_width.interpolate(t),
            AxisType.AXIS_PULSE_RISE_TIME_CYCLES: self.params.pulse_rise_time.interpolate(t),
            AxisType.AXIS_PULSE_INTERVAL_RANDOM_PERCENT: self.params.pulse_interval_random.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_A: self.params.calibrate.a.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_B: self.params.calibrate.b.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_C: self.params.calibrate.c.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_D: self.params.calibrate.d.interpolate(t),
            AxisType.AXIS_CALIBRATION_4_REDUCTION_IN_CENTER: self.params.calibrate.center_reduction.interpolate(t),
        }
