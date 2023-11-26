from PyQt5.QtCore import QSettings
from dataclasses import dataclass

import numpy as np

from stim_math import amplitude_modulation, limits, trig, point_calibration, threephase, fourphase, fivephase
from stim_math.sine_generator import AngleGenerator, AngleGeneratorWithVaryingIPI, PulseGenerator
from stim_math.threephase_coordinate_transform import ThreePhaseCoordinateTransform
from stim_math.threephase_exponent import ThreePhaseExponentAdjustment
from stim_math.threephase_parameter_manager import ThreephaseParameterManager
from qt_ui.preferencesdialog import KEY_AUDIO_CHANNEL_COUNT, KEY_AUDIO_CHANNEL_MAP
import stim_math.pulse


def generate_audio(alpha, beta, theta_carrier,
                   point_calibration=None,
                   point_calibration_2=None,
                   modulation_1=None,
                   modulation_2=None,
                   hardware_calibration=None):
    # TODO: normalize norm(alpha, beta) <= 1

    L, R = threephase.ThreePhaseSignalGenerator.generate(theta_carrier, alpha, beta)

    volume = 1
    if point_calibration is not None:
        volume *= point_calibration.get_scale(alpha, beta)
    if point_calibration_2 is not None:
        volume *= point_calibration_2.get_scale(alpha, beta)
    L *= volume
    R *= volume

    if modulation_1 is not None:
        L, R = modulation_1.modulate(L, R)
    if modulation_2 is not None:
        L, R = modulation_2.modulate(L, R)

    if hardware_calibration is not None:
        L, R = hardware_calibration.apply_transform(L, R)

    return L, R


class VibrationAlgorithm:
    def __init__(self, params: ThreephaseParameterManager):
        self.params = params
        self.vibration_1_angle = AngleGeneratorWithVaryingIPI()
        self.vibration_2_angle = AngleGeneratorWithVaryingIPI()

    def generate_vibration_signal(self, samplerate, n_samples: int):
        volume = 1

        volume *= self._calculate_modulation(
            samplerate, n_samples,
            self.params.vibration_1_enabled.last_value(),
            self.params.vibration_1_frequency.last_value(),
            self.params.vibration_1_strength.last_value(),
            self.params.vibration_1_left_right_bias.last_value(),
            self.params.vibration_1_high_low_bias.last_value(),
            self.params.vibration_1_random.last_value(),
            self.vibration_1_angle,
        )

        volume *= self._calculate_modulation(
            samplerate, n_samples,
            self.params.vibration_2_enabled.last_value(),
            self.params.vibration_2_frequency.last_value(),
            self.params.vibration_2_strength.last_value(),
            self.params.vibration_2_left_right_bias.last_value(),
            self.params.vibration_2_high_low_bias.last_value(),
            self.params.vibration_2_random.last_value(),
            self.vibration_2_angle
        )

        return volume

    def generate_vibration_float(self, samplerate, n_samples):
        volume = self.generate_vibration_signal(samplerate, n_samples)
        try:
            return volume[0]
        except TypeError:
            return volume

    def _calculate_modulation(self, samplerate, n_samples, is_enabled,
                              modulation_frequency, modulation_strength,
                              modulation_left_right_bias, modulation_high_low_bias,
                              modulation_random,
                              angle_generator):
        if not is_enabled or modulation_frequency == 0:
            return 1

        modulation_frequency = np.clip(modulation_frequency,
                                       limits.ModulationFrequency.min,
                                       limits.ModulationFrequency.max)
        theta = angle_generator.generate(n_samples, modulation_frequency, samplerate, modulation_random)
        modulation = amplitude_modulation.SineModulation(
            theta,
            modulation_strength,
            modulation_left_right_bias,
            modulation_high_low_bias,
        )
        return modulation.get_modulation_signal()


class ThreePhasePositionParameters:
    def __init__(self, params: ThreephaseParameterManager):
        self.params = params

    def get_position(self, command_timeline):
        alpha = self.params.alpha.interpolate(command_timeline)
        beta = self.params.beta.interpolate(command_timeline)

        # normalize (alpha, beta) to be within the unit circle.
        norm = np.clip(trig.norm(alpha, beta), 1.0, None)
        alpha /= norm
        beta /= norm

        # mobius transform...
        z = alpha + beta * 1j
        a = self.params.focus_alpha.last_value() + self.params.focus_beta.last_value() * 1j
        z = (z - a) / (1 - np.conj(a) * z)
        alpha = z.real
        beta = z.imag

        if self.params.transform_enabled.last_value():
            transform = ThreePhaseCoordinateTransform(
                self.params.transform_rotation_degrees.last_value(),
                self.params.transform_mirror.last_value(),
                self.params.transform_top_limit.last_value(),
                self.params.transform_bottom_limit.last_value(),
                self.params.transform_left_limit.last_value(),
                self.params.transform_right_limit.last_value(),
            )
            alpha, beta = transform.transform(alpha, beta)
            norm = np.clip(trig.norm(alpha, beta), 1.0, None)
            alpha /= norm
            beta /= norm

        return alpha, beta


class MultiPhaseAlgorithm:
    def __init__(self):
        settings = QSettings()
        self.channel_count = settings.value(KEY_AUDIO_CHANNEL_COUNT, 8, int)
        try:
            map = settings.value(KEY_AUDIO_CHANNEL_MAP, '0, 1, 2, 3', str)
            self.channel_map = [int(x) for x in map.split(',')]
        except ValueError:
            self.channel_map = [0, 1, 2, 3]


class ThreePhaseAlgorithm:
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__()
        self.params = params
        self.vibration = VibrationAlgorithm(params)
        self.carrier_angle = AngleGenerator()
        self.position_params = ThreePhasePositionParameters(params)

    def preferred_channel_count(self):
        return [2]

    def channel_mapping(self, channel_count):
        return [0, 1]

    def generate_audio(self, samplerate, timeline: np.ndarray, command_timeline: np.ndarray):
        volume = \
            np.clip(self.params.ramp_volume.last_value(), 0, 1) * \
            np.clip(self.params.volume.last_value(), 0, 1) * \
            np.clip(self.params.inactivity_volume.last_value(), 0, 1)
        volume *= self.vibration.generate_vibration_signal(samplerate, len(timeline))

        frequency = self.params.mk312_carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Mk312CarrierFrequency.min, limits.Mk312CarrierFrequency.max)
        theta_carrier = self.carrier_angle.generate(len(timeline), frequency, samplerate)

        alpha, beta = self.position_params.get_position(command_timeline)

        # center scaling
        center_calib = point_calibration.CenterCalibration(self.params.calibration_center.last_value())
        volume *= center_calib.get_scale(alpha, beta)

        # exponent transform
        transform = ThreePhaseExponentAdjustment(self.params.threephase_exponent.last_value())
        volume *= transform.get_scale(alpha, beta)

        # hardware calibration
        hw = threephase.ThreePhaseHardwareCalibration(self.params.calibration_neutral.last_value(),
                                                      self.params.calibration_right.last_value())

        tp = threephase.ThreePhaseSignalGenerator()
        L, R = tp.generate(theta_carrier, alpha, beta)
        L, R = hw.apply_transform(L, R)
        L *= volume
        R *= volume
        return L, R


class FourPhaseAlgorithm(MultiPhaseAlgorithm):
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__(params)
        self.params = params
        self.vibration = VibrationAlgorithm(params)
        self.carrier_angle = AngleGenerator()

    def preferred_channel_count(self):
        return [self.channel_count]
        # return [3, 4, 6, 8]

    def channel_mapping(self, channel_count):
        return self.channel_map[:3]
        # return [0, 1, 2]

    def generate_audio(self, samplerate, timeline: np.ndarray, command_timeline: np.ndarray):
        volume = \
            np.clip(self.params.ramp_volume.last_value(), 0, 1) * \
            np.clip(self.params.volume.last_value(), 0, 1) * \
            np.clip(self.params.inactivity_volume.last_value(), 0, 1)
        volume *= self.vibration.generate_vibration_signal(samplerate, len(timeline))

        frequency = self.params.mk312_carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Mk312Carrier.min, limits.Mk312Carrier.max)
        theta_carrier = self.carrier_angle.generate(len(timeline), frequency, samplerate)

        e1 = self.params.e1.interpolate(command_timeline)
        e2 = self.params.e2.interpolate(command_timeline)
        e3 = self.params.e3.interpolate(command_timeline)
        e4 = self.params.e4.interpolate(command_timeline)
        fp = fourphase.FourPhaseSignalGenerator()
        a, b, c, d = fp.generate_from_electrode_amplitudes(theta_carrier, e1, e2, e3, e4)
        fpc = fourphase.FourPhaseHardwareCalibration(
            self.params.resistance_t.last_value(),
            self.params.resistance_s1.last_value(),
            self.params.resistance_s2.last_value(),
            self.params.resistance_s3.last_value(),
            self.params.resistance_s4.last_value(),
        )
        c1, c2, c3 = fpc.transform(a, b, c, d)
        c1 *= volume
        c2 *= volume
        c3 *= volume
        return c1, c2, c3


class FivePhaseAlgorithm(MultiPhaseAlgorithm):
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__(params)
        self.params = params
        self.vibration = VibrationAlgorithm(params)
        self.carrier_angle = AngleGenerator()

    def preferred_channel_count(self):
        return [self.channel_count]
        # return [4, 6, 8]

    def channel_mapping(self, channel_count):
        return self.channel_map[:4]
        # return [0, 1, 6, 7]

    def generate_audio(self, samplerate, timeline: np.ndarray, command_timeline: np.ndarray):
        volume = \
            np.clip(self.params.ramp_volume.last_value(), 0, 1) * \
            np.clip(self.params.volume.last_value(), 0, 1) * \
            np.clip(self.params.inactivity_volume.last_value(), 0, 1)
        volume *= self.vibration.generate_vibration_signal(samplerate, len(timeline))

        frequency = self.params.mk312_carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Mk312CarrierFrequency.min, limits.Mk312CarrierFrequency.max)
        theta_carrier = self.carrier_angle.generate(len(timeline), frequency, samplerate)

        e1 = self.params.e1.interpolate(command_timeline)
        e2 = self.params.e2.interpolate(command_timeline)
        e3 = self.params.e3.interpolate(command_timeline)
        e4 = self.params.e4.interpolate(command_timeline)
        e5 = self.params.e5.interpolate(command_timeline)
        fp = fivephase.FivePhaseSignalGenerator()
        a, b, c, d, e = fp.generate_from_electrode_amplitudes(theta_carrier, e1, e2, e3, e4, e5)
        fpc = fivephase.FivePhaseHardwareCalibration(
            self.params.resistance_t.last_value(),
            self.params.resistance_s1.last_value(),
            self.params.resistance_s2.last_value(),
            self.params.resistance_s3.last_value(),
            self.params.resistance_s4.last_value(),
            self.params.resistance_s5.last_value(),
        )

        c1, c2, c3, c4 = fpc.transform(a, b, c, d, e)
        c1 *= volume
        c2 *= volume
        c3 *= volume
        c4 *= volume
        return c1, c2, c3, c4


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
        center_calib = point_calibration.CenterCalibration(self.params.calibration_center.last_value())
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

