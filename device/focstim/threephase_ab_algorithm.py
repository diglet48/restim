import time

import numpy as np

from stim_math.audio_gen.base_classes import RemoteGenerationAlgorithm
from stim_math.audio_gen.params import SafetyParamsFOC, ABTestFOCStimParams
from stim_math.pulse_frequency_calibration import PulseFrequencyCalibration
from stim_math.tau_calibration import TauCalibration
from stim_math.threephase_position import ThreePhasePosition
from stim_math.axis import AbstractMediaSync
from device.focstim.constants_pb2 import AxisType
from stim_math import limits
import stim_math.burst_gap


class FOCStimThreephaseABTestAlgorithm(RemoteGenerationAlgorithm):
    def __init__(self, media: AbstractMediaSync, params: ABTestFOCStimParams, safety_limits: SafetyParamsFOC, waveform_change_callback):
        super().__init__()
        self.media = media
        self.params = params
        self.safety_limits = safety_limits
        self.position_params = ThreePhasePosition(params.position, params.transform)
        self.callback = waveform_change_callback

        self.is_A_cycle = True
        self.seconds_generated = 0
        self.last_update_time = 0


        epsilon = 0.0001
        assert safety_limits.waveform_amplitude_amps >= (limits.WaveformAmpltiudeFOC.min - epsilon)
        assert safety_limits.waveform_amplitude_amps <= (limits.WaveformAmpltiudeFOC.max + epsilon)

        self.sensor_node = None

    def outputs(self):
        return 3

    def parameter_dict(self) -> dict:
        t = time.time()

        dt = t - self.last_update_time
        self.last_update_time = t
        self.seconds_generated += dt

        if self.is_A_cycle:
            target_train_length = self.params.a_train_duration.last_value()
            if self.seconds_generated >= target_train_length:
                self.is_A_cycle = False
                self.seconds_generated = 0
                self.callback(False)
        else:
            target_train_length = self.params.b_train_duration.last_value()
            if self.seconds_generated >= target_train_length:
                self.is_A_cycle = True
                self.seconds_generated = 0
                self.callback(True)


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

        if self.is_A_cycle:
            volume *= np.clip(self.params.a_volume.last_value(), 0, 1)
            carrier_frequency = self.params.a_carrier_frequency.interpolate(t)
            carrier_frequency = np.clip(carrier_frequency, minimum_frequency, maximum_frequency)
            pulse_frequency = self.params.a_pulse_frequency.interpolate(t)
            pulse_width = self.params.a_pulse_width.interpolate(t)
            pulse_interval_random = self.params.a_pulse_interval_random.interpolate(t)
            pulse_rise_time = self.params.a_pulse_rise_time.interpolate(t)
        else:
            volume *= np.clip(self.params.b_volume.last_value(), 0, 1)
            carrier_frequency = self.params.b_carrier_frequency.interpolate(t)
            carrier_frequency = np.clip(carrier_frequency, minimum_frequency, maximum_frequency)
            pulse_frequency = self.params.b_pulse_frequency.interpolate(t)
            pulse_width = self.params.b_pulse_width.interpolate(t)
            pulse_interval_random = self.params.b_pulse_interval_random.interpolate(t)
            pulse_rise_time = self.params.b_pulse_rise_time.interpolate(t)

        pulse_frequency = np.clip(pulse_frequency, limits.PulseFrequency.min, limits.PulseFrequency.max)
        pulse_width = np.clip(pulse_width.interpolate(t), limits.PulseWidth.min, limits.PulseWidth.max)

        # convert burst freq to pulse freq (if applicable) and limit gap to 5ms
        pulse_width_in_s = np.clip(pulse_width / carrier_frequency, None, limits.PulseDuration.max)
        if self.params.enable_burst_gap.last_value():
            pause_width_in_s = np.clip(1 / pulse_frequency,
                                       limits.InterPulseIntervalDuration.min, limits.InterPulseIntervalDuration.max)
        else:
            pause_width_in_s = np.clip(1 / pulse_frequency - pulse_width_in_s,
                                       limits.InterPulseIntervalDuration.min, limits.InterPulseIntervalDuration.max)
        pulse_frequency = 1 / (pulse_width_in_s + pause_width_in_s)

        carrier_calibration = TauCalibration.derating_factor(maximum_frequency, carrier_frequency, tau)
        volume *= np.clip(carrier_calibration, 0, 1)

        if self.params.enable_burst_gap.last_value():
            pulse_frequency = stim_math.burst_gap.burst_gap_frequency_to_pulse_frequency(carrier_frequency, pulse_frequency, pulse_width)

        if self.params.enable_pulse_frequency_adjustment.last_value():
            pulse_frequency_calibration = PulseFrequencyCalibration.scale(pulse_frequency)
            volume *= np.clip(pulse_frequency_calibration, 0, 1)

        alpha = self.position_params.position_params.alpha.interpolate(t)
        beta = self.position_params.position_params.beta.interpolate(t)

        if self.sensor_node:
            d = {'volume': volume, 'alpha': alpha, 'beta': beta}
            self.sensor_node.process(d)
            # safety: new volume must be less than original
            volume = np.clip(d['volume'], 0, volume)
            alpha = d['alpha']
            beta = d['beta']

        alpha, beta = self.position_params.transform_position(alpha, beta)

        if not self.media.is_playing():
            volume *= 0

        return {
            AxisType.AXIS_POSITION_ALPHA: alpha,
            AxisType.AXIS_POSITION_BETA: beta,
            AxisType.AXIS_WAVEFORM_AMPLITUDE_AMPS: volume * self.safety_limits.waveform_amplitude_amps,
            AxisType.AXIS_CARRIER_FREQUENCY_HZ: carrier_frequency,
            AxisType.AXIS_PULSE_FREQUENCY_HZ: pulse_frequency,
            AxisType.AXIS_PULSE_WIDTH_IN_CYCLES: pulse_width,
            AxisType.AXIS_PULSE_RISE_TIME_CYCLES: pulse_rise_time,
            AxisType.AXIS_PULSE_INTERVAL_RANDOM_PERCENT: pulse_interval_random,
            AxisType.AXIS_CALIBRATION_3_CENTER: self.params.calibrate.center.interpolate(t),
            AxisType.AXIS_CALIBRATION_3_UP: self.params.calibrate.neutral.interpolate(t),
            AxisType.AXIS_CALIBRATION_3_LEFT: self.params.calibrate.right.interpolate(t),
        }
