from dataclasses import dataclass

import numpy as np

import stim_math.pulse
import stim_math.threephase
from stim_math import threephase
from stim_math.audio_gen.various import ThreePhasePositionParameters, VibrationAlgorithm
from stim_math.threephase_parameter_manager import ThreephaseParameterManager


@dataclass
class PulseInfo:
    polarity: float     # 1 or -1
    start_angle: float  # in rad
    carrier_frequency: float
    pulse_width_in_carrier_cycles: float
    position: tuple[float]
    pause_length_in_s: float
    volume: float

    def pulse_length_in_samples(self, samplerate):
        return int(samplerate / self.carrier_frequency * self.pulse_width_in_carrier_cycles)

    def pause_length_in_samples(self, samplerate):
        return int(samplerate * self.pause_length_in_s)

    def total_length_in_samples(self, samplerate):
        return self.pulse_length_in_samples(samplerate) + self.pause_length_in_samples(samplerate)


class ThreePhasePulseBasedAlgorithmBase:
    def __init__(self, params: ThreephaseParameterManager):
        self._sample_buffer = np.zeros((2, 0), dtype=np.float32)
        self.params = params

    def preferred_channel_count(self):
        return [2]

    def channel_mapping(self, channel_count):
        return [0, 1]

    def next_pulse_data(self, samplerate, at_time: float, at_command_time: float) -> PulseInfo:
        raise NotImplementedError()

    def generate_audio(self, samplerate, timeline: np.ndarray, command_timeline: np.ndarray):
        while self._sample_buffer.shape[1] < len(timeline):
            i = self._sample_buffer.shape[1]
            next_pulse = self.next_pulse_data(samplerate, timeline[i], command_timeline[i])
            self.add_next_pulse_to_audio_buffer(samplerate, next_pulse)

        n = len(timeline)
        L, R = self._sample_buffer[:, :n]
        self._sample_buffer = self._sample_buffer[:, n:]
        return L, R

    def add_next_pulse_to_audio_buffer(self, samplerate, pulse: PulseInfo):
        pulse_envelope = stim_math.pulse.create_pulse_envelope_half_circle(pulse.pulse_length_in_samples(samplerate))

        pause = stim_math.pulse.create_pause(pulse.pause_length_in_samples(samplerate))

        theta = pulse.start_angle + np.linspace(0, 2 * np.pi * pulse.pulse_width_in_carrier_cycles,
                                                len(pulse_envelope)) * pulse.polarity
        L, R = threephase.ThreePhaseSignalGenerator.generate(
            theta, np.full_like(theta, pulse.position[0]), np.full_like(theta, pulse.position[1]))

        # L[:] = 1
        # R[:] = 1
        # pulse_envelope[:] = 1

        # center scaling
        center_calib = stim_math.threephase.ThreePhaseCenterCalibration(self.params.calibration_center.last_value())
        pulse_envelope *= center_calib.get_scale(pulse.position[0], pulse.position[1])

        # hardware calibration
        hw = threephase.ThreePhaseHardwareCalibration(self.params.calibration_neutral.last_value(),
                                                      self.params.calibration_right.last_value())
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
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__(params)
        self.position_params = ThreePhasePositionParameters(params)
        self.vibration = VibrationAlgorithm(params)
        self.seq = 0

    def next_pulse_data(self, samplerate, at_time: float, at_command_time: float) -> PulseInfo:
        self.seq += 1

        volume = \
            np.clip(self.params.ramp_volume.last_value(), 0, 1) * \
            np.clip(self.params.volume.last_value(), 0, 1) * \
            np.clip(self.params.inactivity_volume.last_value(), 0, 1)

        pulse_carrier_freq = self.params.pulse_carrier_frequency.interpolate(at_command_time)
        pulse_width = self.params.pulse_width.interpolate(at_command_time)
        pulse_freq = self.params.pulse_frequency.interpolate(at_command_time)
        pause_duration = np.clip(1 / pulse_freq - pulse_width / pulse_carrier_freq, 0, None)

        random = self.params.pulse_interval_random.interpolate(at_command_time)
        pause_duration = pause_duration * np.random.uniform(1 - random, 1 + random)

        alpha, beta = self.position_params.get_position(at_command_time)

        # exponent transform. TODO: decide whether to keep
        # transform = ThreePhaseExponentAdjustment(self.params.threephase_exponent.last_value())
        # volume *= transform.get_scale(alpha, beta)

        pulse = PulseInfo(
            self.polarity(at_command_time),
            self.phase_offset(),
            pulse_carrier_freq,
            pulse_width,
            (alpha, beta),
            pause_duration,
            volume,
        )
        # pulse = self.apply_device_emulation(pulse) # Reduces volume by 15%
        pulse = self.apply_vibration(samplerate, pulse)
        return pulse

    def apply_device_emulation(self, pulse: PulseInfo) -> PulseInfo:
        alpha, beta = pulse.position
        volume = pulse.volume

        if self.params.device_emulation_mode.last_value() in (1, 2):
            r = np.sqrt(alpha**2 + beta**2)
            projection_on_complex_plane = np.array([
                [1, 0],
                [-.5, np.sqrt(3) / 2],
                [-.5, -np.sqrt(3) / 2],
            ]) @ np.array([
                [2 - r + alpha, beta],
                [beta, 2 - r - alpha]
            ]) * 0.5

            c1 = np.linalg.norm(projection_on_complex_plane[0] - projection_on_complex_plane[1]) / np.sqrt(3)
            c2 = np.linalg.norm(projection_on_complex_plane[0] - projection_on_complex_plane[2]) / np.sqrt(3)
            c3 = np.linalg.norm(projection_on_complex_plane[1] - projection_on_complex_plane[2]) / np.sqrt(3)

            # emulation mode 1, 'et312'
            if self.params.device_emulation_mode.last_value() == 1:
                channel = self.seq % 2
            else: # emulation mode 2 'neostim'
                channel = self.seq % 3

            if channel == 2:
                alpha, beta = (1, 0)
                volume *= c3
            if channel == 0:
                alpha, beta = (-1/2, -np.sqrt(3)/2)
                volume *= c1
            if channel == 1:
                alpha, beta = (-1/2, np.sqrt(3)/2)
                volume *= c2
        else:
            volume *= 0.85

        pulse.position = (alpha, beta)
        pulse.volume = volume
        return pulse

    def apply_vibration(self, samplerate, pulse: PulseInfo) -> PulseInfo:
        pulse.volume *= self.vibration.generate_vibration_float(samplerate, pulse.total_length_in_samples(samplerate))
        return pulse

    def polarity(self, at_command_time):
        polarity = self.params.polarity.interpolate(at_command_time)
        if polarity not in (-1, 1):
            polarity = np.random.choice((-1, 1))
        return polarity

    def phase_offset(self):
        phase_offset_increment = self.params.pulse_phase_offset_increment.last_value()
        if phase_offset_increment == 0.0:
            phase_offset = np.random.uniform(0, np.pi * 2)
        else:
            phase_offset = (phase_offset_increment * self.seq) % (np.pi * 2)
        return phase_offset
