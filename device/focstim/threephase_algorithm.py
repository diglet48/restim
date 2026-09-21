import time

import numpy as np

from stim_math.audio_gen.base_classes import RemoteGenerationAlgorithm
from stim_math.audio_gen.params import FOCStimParams, SafetyParamsFOC
from stim_math.pulse_frequency_calibration import PulseFrequencyCalibration
from stim_math.tau_calibration import TauCalibration
from stim_math.threephase_position import ThreePhasePosition
from stim_math.axis import AbstractMediaSync
from stim_math.threephase import ud_lr_to_intensity_ratio
import stim_math.burst_gap
from device.focstim.constants_pb2 import AxisType
from stim_math import limits


class FOCStimThreephaseAlgorithm(RemoteGenerationAlgorithm):
    def __init__(self, media: AbstractMediaSync, params: FOCStimParams, safety_limits: SafetyParamsFOC):
        super().__init__()
        self.media = media
        self.params = params
        self.safety_limits = safety_limits
        self.position_params = ThreePhasePosition(params.position, params.transform)

        epsilon = 0.0001
        assert safety_limits.waveform_amplitude_amps >= (limits.WaveformAmpltiudeFOC.min - epsilon)
        assert safety_limits.waveform_amplitude_amps <= (limits.WaveformAmpltiudeFOC.max + epsilon)

        self.sensor_node = None

    def outputs(self):
        return 3

    def parameter_dict(self) -> dict:
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

        pulse_frequency = self.params.pulse_frequency.interpolate(t)
        pulse_width = self.params.pulse_width.interpolate(t)
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


        calib = ud_lr_to_intensity_ratio(self.params.calibrate.neutral.interpolate(t), self.params.calibrate.right.interpolate(t))
        calib = 10 * np.log10(calib)    # convert ratio to db
        calib_a, calib_b, calib_c = calib
        center_reduction =  1 - 10 ** (self.params.calibrate.center.interpolate(t) / 10) # convert db to percent reduction

        return {
            AxisType.AXIS_POSITION_ALPHA: alpha,
            AxisType.AXIS_POSITION_BETA: beta,
            AxisType.AXIS_WAVEFORM_AMPLITUDE_AMPS: volume * self.safety_limits.waveform_amplitude_amps,
            AxisType.AXIS_CARRIER_FREQUENCY_HZ: carrier_frequency,
            AxisType.AXIS_PULSE_FREQUENCY_HZ: pulse_frequency,
            AxisType.AXIS_PULSE_WIDTH_IN_CYCLES: pulse_width,
            AxisType.AXIS_PULSE_RISE_TIME_CYCLES: self.params.pulse_rise_time.interpolate(t),
            AxisType.AXIS_PULSE_INTERVAL_RANDOM_PERCENT: self.params.pulse_interval_random.interpolate(t),
            AxisType.AXIS_CALIBRATION_3_A: calib_a,
            AxisType.AXIS_CALIBRATION_3_B: calib_b,
            AxisType.AXIS_CALIBRATION_3_C: calib_c,
            AxisType.AXIS_CALIBRATION_3_REDUCTION_IN_CENTER: center_reduction,
        }
