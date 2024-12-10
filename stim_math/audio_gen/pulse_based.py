from dataclasses import dataclass

import numpy as np

import stim_math.pulse
import stim_math.threephase
from stim_math.audio_gen.base_classes import AudioGenerationAlgorithm
from stim_math import threephase
from stim_math.audio_gen.various import ThreePhasePosition, VibrationAlgorithm
from stim_math.audio_gen.params import ThreephasePulsebasedAlgorithmParams, ThreephaseCalibrationParams, SafetyParams, ThreephaseABTestAlgorithmParams
from stim_math.axis import AbstractMediaSync
from stim_math import limits


@dataclass
class PulseInfo:
    polarity: float     # 1 or -1
    start_angle: float  # in rad
    carrier_frequency: float
    pulse_width_in_carrier_cycles: float
    rise_time_in_carrier_cycles: float
    position: tuple[float]
    pause_length_in_s: float
    volume: float

    def pulse_length_in_samples(self, samplerate):
        return int(samplerate / self.carrier_frequency * self.pulse_width_in_carrier_cycles)

    def pause_length_in_samples(self, samplerate):
        return int(samplerate * self.pause_length_in_s)

    def total_length_in_samples(self, samplerate):
        return self.pulse_length_in_samples(samplerate) + self.pause_length_in_samples(samplerate)


class ThreePhasePulseBasedAlgorithmBase(AudioGenerationAlgorithm):
    def __init__(self, media: AbstractMediaSync, calibration: ThreephaseCalibrationParams):
        super(ThreePhasePulseBasedAlgorithmBase, self).__init__()
        self._sample_buffer = np.zeros((2, 0), dtype=np.float32)
        self.media = media
        self.calibration = calibration

    def channel_count(self) -> int:
        return 2

    def next_pulse_data(self, samplerate, at_time: float, at_command_time: float) -> PulseInfo:
        raise NotImplementedError()

    def generate_audio(self, samplerate, steady_clock: np.ndarray, system_time_estimate: np.ndarray):
        while self._sample_buffer.shape[1] < len(steady_clock):
            i = self._sample_buffer.shape[1]
            next_pulse = self.next_pulse_data(samplerate, steady_clock[i], system_time_estimate[i])
            self.add_next_pulse_to_audio_buffer(samplerate, next_pulse)

        n = len(steady_clock)
        L, R = self._sample_buffer[:, :n]
        self._sample_buffer = self._sample_buffer[:, n:]
        return L, R

    def add_next_pulse_to_audio_buffer(self, samplerate, pulse: PulseInfo):
        pulse_envelope = stim_math.pulse.create_pulse_with_ramp_time(
            pulse.pulse_length_in_samples(samplerate),
            pulse.pulse_width_in_carrier_cycles,
            pulse.rise_time_in_carrier_cycles)

        if not self.media.is_playing():
            # TODO: make more efficient
            pulse_envelope *= 0

        pause = stim_math.pulse.create_pause(pulse.pause_length_in_samples(samplerate))

        theta = pulse.start_angle + np.linspace(0, 2 * np.pi * pulse.pulse_width_in_carrier_cycles,
                                                len(pulse_envelope)) * pulse.polarity
        L, R = threephase.ThreePhaseSignalGenerator.generate(
            theta, np.full_like(theta, pulse.position[0]), np.full_like(theta, pulse.position[1]))

        # L[:] = 1
        # R[:] = 1
        # pulse_envelope[:] = 1

        # center scaling
        center_calib = stim_math.threephase.ThreePhaseCenterCalibration(self.calibration.center.last_value())
        pulse_envelope *= center_calib.get_scale(pulse.position[0], pulse.position[1])

        # hardware calibration
        hw = threephase.ThreePhaseHardwareCalibration(self.calibration.neutral.last_value(),
                                                      self.calibration.right.last_value())
        L, R = hw.apply_transform(L, R)

        pulse_envelope *= pulse.volume
        L *= pulse_envelope
        R *= pulse_envelope

        new_data = np.vstack((
            np.hstack((L, pause)),
            np.hstack((R, pause)),
        ))
        self._sample_buffer = np.hstack((self._sample_buffer, new_data))


class DefaultThreePhasePulseBasedAlgorithm(ThreePhasePulseBasedAlgorithmBase):
    def __init__(self, media: AbstractMediaSync, params: ThreephasePulsebasedAlgorithmParams, safety_limits: SafetyParams):
        super().__init__(media, params.calibrate)
        self.params = params
        self.position_params = ThreePhasePosition(params.position, params.transform)
        self.vibration = VibrationAlgorithm(params.vibration_1, params.vibration_2)
        self.seq = 0
        self.safety_limits = safety_limits
        self.last_pulse_polarity = 1
        self.last_pulse_start_angle = 0

    def next_pulse_data(self, samplerate, at_time: float, system_time_estimate: float) -> PulseInfo:
        self.seq += 1

        volume = \
            np.clip(self.params.volume.master.last_value(), 0, 1) * \
            np.clip(self.params.volume.api.interpolate(system_time_estimate), 0, 1) * \
            np.clip(self.params.volume.inactivity.last_value(), 0, 1) * \
            np.clip(self.params.volume.external.last_value(), 0, 1)

        pulse_carrier_freq = self.params.carrier_frequency.interpolate(system_time_estimate)
        pulse_carrier_freq = np.clip(pulse_carrier_freq,
                                     self.safety_limits.minimum_carrier_frequency,
                                     self.safety_limits.maximum_carrier_frequency)
        pulse_width = self.params.pulse_width.interpolate(system_time_estimate)
        pulse_width = np.clip(pulse_width, limits.PulseWidth.min, limits.PulseWidth.max)
        pulse_freq = self.params.pulse_frequency.interpolate(system_time_estimate)
        pulse_freq = np.clip(pulse_freq, limits.PulseFrequency.min, limits.PulseFrequency.max)
        pulse_rise_time = self.params.pulse_rise_time.interpolate(system_time_estimate)
        pulse_rise_time = np.clip(pulse_rise_time, limits.PulseRiseTime.min, limits.PulseRiseTime.max)

        pause_duration = np.clip(1 / pulse_freq - pulse_width / pulse_carrier_freq, 0, None)

        random = self.params.pulse_interval_random.interpolate(system_time_estimate)
        pause_duration = pause_duration * np.random.uniform(1 - random, 1 + random)

        alpha, beta = self.position_params.get_position(system_time_estimate)

        # exponent transform. TODO: decide whether to keep
        # transform = ThreePhaseExponentAdjustment(self.params.threephase_exponent.last_value())
        # volume *= transform.get_scale(alpha, beta)

        pulse = PulseInfo(
            self.polarity(),
            self.phase_offset(),
            pulse_carrier_freq,
            pulse_width,
            pulse_rise_time,
            (alpha, beta),
            pause_duration,
            volume,
        )
        pulse = self.apply_vibration(system_time_estimate, samplerate, pulse)
        return pulse

    def apply_vibration(self, at_command_time, samplerate, pulse: PulseInfo) -> PulseInfo:
        pulse.volume *= self.vibration.generate_vibration_float(at_command_time, samplerate, pulse.total_length_in_samples(samplerate))
        return pulse

    def polarity(self):
        if self.last_pulse_polarity == 1:
            self.last_pulse_polarity = -1
            return -1
        else:
            self.last_pulse_polarity = 1
            return 1

    def phase_offset(self):
        self.last_pulse_start_angle = (self.last_pulse_start_angle + (np.pi * 2 * 19 / 97)) % (2 * np.pi)  # ~1/5
        return self.last_pulse_start_angle


class ABTestThreePhasePulseBasedAlgorithm(ThreePhasePulseBasedAlgorithmBase):
    def __init__(self, media: AbstractMediaSync, params: ThreephaseABTestAlgorithmParams, safety_limits: SafetyParams, waveform_change_callback):
        super().__init__(media, params.calibrate)
        self.params = params
        self.position_params = ThreePhasePosition(params.position, params.transform)
        self.vibration = VibrationAlgorithm(params.vibration_1, params.vibration_2)
        self.seq = 0
        self.safety_limits = safety_limits
        self.last_pulse_polarity = 1
        self.last_pulse_start_angle = 0
        self.callback = waveform_change_callback

        self.is_A_cycle = True
        self.seconds_generated = 0

    def next_pulse_data(self, samplerate, at_time: float, system_time_estimate: float) -> PulseInfo:
        self.seq += 1
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
            np.clip(self.params.volume.api.interpolate(system_time_estimate), 0, 1) * \
            np.clip(self.params.volume.inactivity.last_value(), 0, 1) * \
            np.clip(self.ab_volume(system_time_estimate), 0, 1) * \
            np.clip(self.params.volume.external.last_value(), 0, 1)

        pulse_carrier_freq = self.carrier_frequency(system_time_estimate)
        pulse_carrier_freq = np.clip(pulse_carrier_freq,
                                     self.safety_limits.minimum_carrier_frequency,
                                     self.safety_limits.maximum_carrier_frequency)
        pulse_width = self.pulse_width(system_time_estimate)
        pulse_width = np.clip(pulse_width, limits.PulseWidth.min, limits.PulseWidth.max)
        pulse_freq = self.pulse_frequency(system_time_estimate)
        pulse_freq = np.clip(pulse_freq, limits.PulseFrequency.min, limits.PulseFrequency.max)
        pulse_rise_time = self.pulse_rise_time(system_time_estimate)
        pulse_rise_time = np.clip(pulse_rise_time, limits.PulseRiseTime.min, limits.PulseRiseTime.max)

        pause_duration = np.clip(1 / pulse_freq - pulse_width / pulse_carrier_freq, 0, None)

        random = self.pulse_interval_random(system_time_estimate)
        pause_duration = pause_duration * np.random.uniform(1 - random, 1 + random)

        alpha, beta = self.position_params.get_position(system_time_estimate)

        # exponent transform. TODO: decide whether to keep
        # transform = ThreePhaseExponentAdjustment(self.params.threephase_exponent.last_value())
        # volume *= transform.get_scale(alpha, beta)

        pulse = PulseInfo(
            self.polarity(),
            self.phase_offset(),
            pulse_carrier_freq,
            pulse_width,
            pulse_rise_time,
            (alpha, beta),
            pause_duration,
            volume,
        )
        pulse = self.apply_vibration(system_time_estimate, samplerate, pulse)
        self.seconds_generated += float(pulse.total_length_in_samples(samplerate)) / samplerate
        return pulse

    def apply_vibration(self, at_command_time, samplerate, pulse: PulseInfo) -> PulseInfo:
        pulse.volume *= self.vibration.generate_vibration_float(at_command_time, samplerate, pulse.total_length_in_samples(samplerate))
        return pulse

    def polarity(self):
        if self.last_pulse_polarity == 1:
            self.last_pulse_polarity = -1
            return -1
        else:
            self.last_pulse_polarity = 1
            return 1

    def phase_offset(self):
        self.last_pulse_start_angle = (self.last_pulse_start_angle + (np.pi * 2 * 19 / 97)) % (2 * np.pi)  # ~1/5
        return self.last_pulse_start_angle

    def ab_volume(self, time):
        if self.is_A_cycle:
            return self.params.a_volume.interpolate(time)
        else:
            return self.params.b_volume.interpolate(time)

    def carrier_frequency(self, time):
        if self.is_A_cycle:
            return self.params.a_carrier_frequency.interpolate(time)
        else:
            return self.params.b_carrier_frequency.interpolate(time)

    def pulse_frequency(self, time):
        if self.is_A_cycle:
            return self.params.a_pulse_frequency.interpolate(time)
        else:
            return self.params.b_pulse_frequency.interpolate(time)

    def pulse_width(self, time):
        if self.is_A_cycle:
            return self.params.a_pulse_width.interpolate(time)
        else:
            return self.params.b_pulse_width.interpolate(time)

    def pulse_rise_time(self, time):
        if self.is_A_cycle:
            return self.params.a_pulse_rise_time.interpolate(time)
        else:
            return self.params.b_pulse_rise_time.interpolate(time)

    def pulse_interval_random(self, time):
        if self.is_A_cycle:
            return self.params.a_pulse_interval_random.interpolate(time)
        else:
            return self.params.b_pulse_interval_random.interpolate(time)