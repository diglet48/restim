import numpy as np

from stim_math import limits, amplitude_modulation, trig
from stim_math.sine_generator import AngleGeneratorWithVaryingIPI
from stim_math.threephase_coordinate_transform import ThreePhaseCoordinateTransform, \
    ThreePhaseCoordinateTransformMapToEdge
from stim_math.threephase_parameter_manager import ThreephaseParameterManager


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
        if self.params.map_to_edge_enabled.last_value():
            transform = ThreePhaseCoordinateTransformMapToEdge(
                self.params.map_to_edge_start.last_value(),
                self.params.map_to_edge_length.last_value(),
                self.params.map_to_edge_invert.last_value(),
            )
            alpha, beta = transform.transform(alpha, beta)
            norm = np.clip(trig.norm(alpha, beta), 1.0, None)
            alpha /= norm
            beta /= norm

        return alpha, beta
