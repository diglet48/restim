import numpy as np

from stim_math import limits, amplitude_modulation, trig
from stim_math.sine_generator import AngleGeneratorWithVaryingIPI
from stim_math.threephase_coordinate_transform import ThreePhaseCoordinateTransform, \
    ThreePhaseCoordinateTransformMapToEdge

from stim_math.audio_gen.params import VibrationParams, ThreephasePositionParams, ThreephasePositionTransformParams, \
    FourphaseIntensityParams


class VibrationAlgorithm:
    def __init__(self, vib_1: VibrationParams, vib_2: VibrationParams):
        self.vib_1 = vib_1
        self.vibration_1_angle = AngleGeneratorWithVaryingIPI()
        self.vib_2 = vib_2
        self.vibration_2_angle = AngleGeneratorWithVaryingIPI()

    def generate_vibration_signal(self, command_timeline, samplerate, n_samples: int):
        volume = 1

        volume *= self._calculate_modulation(
            command_timeline,
            samplerate, n_samples,
            self.vib_1, self.vibration_1_angle,
        )

        volume *= self._calculate_modulation(
            command_timeline,
            samplerate, n_samples,
            self.vib_2, self.vibration_2_angle,
        )

        return volume

    def generate_vibration_float(self, command_timeline, samplerate, n_samples):
        volume = self.generate_vibration_signal(command_timeline, samplerate, n_samples)
        try:
            return volume[0]
        except TypeError:
            return volume

    def _calculate_modulation(self, command_timeline, samplerate, n_samples, params: VibrationParams, angle_generator):
        is_enabled = params.enabled.last_value()
        modulation_frequency = params.frequency.interpolate(command_timeline)
        modulation_strength = params.strength.interpolate(command_timeline)
        modulation_left_right_bias = params.left_right_bias.interpolate(command_timeline)
        modulation_high_low_bias = params.high_low_bias.interpolate(command_timeline)
        modulation_random = params.high_low_bias.interpolate(command_timeline)

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


class ThreePhasePosition:
    def __init__(self, position: ThreephasePositionParams, transform: ThreephasePositionTransformParams):
        self.position_params = position
        self.transform_params = transform

    def get_position(self, command_timeline):
        alpha = self.position_params.alpha.interpolate(command_timeline)
        beta = self.position_params.beta.interpolate(command_timeline)
        return self.transform_position(alpha, beta)

    def transform_position(self, alpha, beta):

        # normalize (alpha, beta) to be within the unit circle.
        norm = np.clip(trig.norm(alpha, beta), 1.0, None)
        alpha /= norm
        beta /= norm

        # # mobius transform...
        # z = alpha + beta * 1j
        # a = self.params.focus_alpha.last_value() + self.params.focus_beta.last_value() * 1j
        # z = (z - a) / (1 - np.conj(a) * z)
        # alpha = z.real
        # beta = z.imag

        if self.transform_params.transform_enabled.last_value():
            transform = ThreePhaseCoordinateTransform(
                self.transform_params.transform_rotation_degrees.last_value(),
                self.transform_params.transform_mirror.last_value(),
                self.transform_params.transform_top_limit.last_value(),
                self.transform_params.transform_bottom_limit.last_value(),
                self.transform_params.transform_left_limit.last_value(),
                self.transform_params.transform_right_limit.last_value(),
            )
            alpha, beta = transform.transform(alpha, beta)
            norm = np.clip(trig.norm(alpha, beta), 1.0, None)
            alpha /= norm
            beta /= norm
        if self.transform_params.map_to_edge_enabled.last_value():
            transform = ThreePhaseCoordinateTransformMapToEdge(
                self.transform_params.map_to_edge_start.last_value(),
                self.transform_params.map_to_edge_length.last_value(),
                self.transform_params.map_to_edge_invert.last_value(),
            )
            alpha, beta = transform.transform(alpha, beta)
            norm = np.clip(trig.norm(alpha, beta), 1.0, None)
            alpha /= norm
            beta /= norm

        return alpha, beta

class FourPhaseIntensity:
    def __init__(self, position: FourphaseIntensityParams):
        self.position_params = position

    def get_position(self, command_timeline):
        a = np.clip(self.position_params.a.interpolate(command_timeline), 0, 1)
        b = np.clip(self.position_params.b.interpolate(command_timeline), 0, 1)
        c = np.clip(self.position_params.c.interpolate(command_timeline), 0, 1)
        d = np.clip(self.position_params.d.interpolate(command_timeline), 0, 1)

        return a, b, c, d
