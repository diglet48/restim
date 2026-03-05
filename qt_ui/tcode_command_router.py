from dataclasses import dataclass
import logging
import math
import time

import numpy as np
from PySide6.QtCore import QObject, Signal

from net.tcode import TCodeCommand
from stim_math.axis import AbstractAxis
from stim_math.transforms import half_angle_to_full
from stim_math.transforms_4 import abc_to_e1234, apply_electrode_curves, position_based_gamma

from qt_ui.models.funscript_kit import FunscriptKitModel, FunscriptKitItem
from qt_ui.device_wizard.axes import AxisEnum

logger = logging.getLogger('restim.tcode')


@dataclass
class Route:
    axis: AbstractAxis
    low: float
    high: float

    def remap(self, value):
        return min(max(value, 0.0), 1.0) * (self.high - self.low) + self.low


class TCodeCommandRouter(QObject):
    # Emitted when a TCode command writes to an axis. Passes the axis object.
    axis_updated = Signal(object)

    def __init__(self,
                 alpha: AbstractAxis,
                 beta: AbstractAxis,

                 volume_api: AbstractAxis,
                 volume_external: AbstractAxis,

                 carrier_frequency: AbstractAxis,   # either pulse of continuous

                 pulse_frequency: AbstractAxis,
                 pulse_width: AbstractAxis,
                 pulse_interval_random: AbstractAxis,
                 pulse_rise_time: AbstractAxis,

                 vibration_1_frequency: AbstractAxis,
                 vibration_1_strength: AbstractAxis,
                 vibration_1_left_right_bias: AbstractAxis,
                 vibration_1_high_low_bias: AbstractAxis,
                 vibration_1_random: AbstractAxis,

                 vibration_2_frequency: AbstractAxis,
                 vibration_2_strength: AbstractAxis,
                 vibration_2_left_right_bias: AbstractAxis,
                 vibration_2_high_low_bias: AbstractAxis,
                 vibration_2_random: AbstractAxis,

                 intensity_a: AbstractAxis,
                 intensity_b: AbstractAxis,
                 intensity_c: AbstractAxis,
                 intensity_d: AbstractAxis,
                 ):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.volume_api = volume_api
        self.volume_external = volume_external
        self.carrier_frequency = carrier_frequency
        self.pulse_frequency = pulse_frequency
        self.pulse_width = pulse_width
        self.pulse_interval_random = pulse_interval_random
        self.pulse_rise_time = pulse_rise_time
        self.vibration_1_frequency = vibration_1_frequency
        self.vibration_1_strength = vibration_1_strength
        self.vibration_1_left_right_bias = vibration_1_left_right_bias
        self.vibration_1_high_low_bias = vibration_1_high_low_bias
        self.vibration_1_random = vibration_1_random
        self.vibration_2_frequency = vibration_2_frequency
        self.vibration_2_strength = vibration_2_strength
        self.vibration_2_left_right_bias = vibration_2_left_right_bias
        self.vibration_2_high_low_bias = vibration_2_high_low_bias
        self.vibration_2_random = vibration_2_random

        self.intensity_a = intensity_a
        self.intensity_b = intensity_b
        self.intensity_c = intensity_c
        self.intensity_d = intensity_d

        # State for real-time gamma derivation (speed mode)
        self._prev_alpha = 0.0
        self._prev_beta = 0.0
        self._prev_time = time.monotonic()
        self._running_max_speed = 1.0  # running max for normalization, avoids needing global lookahead
        self._speed_decay = 0.995      # slow decay per update so running max adapts over time

        self.mapping = {}
        self.reload_kit()

    def reload_kit(self):
        axis_enum_to_axis = {
            AxisEnum.POSITION_ALPHA: self.alpha,
            AxisEnum.POSITION_BETA: self.beta,

            AxisEnum.VOLUME_API: self.volume_api,
            AxisEnum.VOLUME_EXTERNAL: self.volume_external,
            AxisEnum.CARRIER_FREQUENCY: self.carrier_frequency,

            AxisEnum.PULSE_FREQUENCY: self.pulse_frequency,
            AxisEnum.PULSE_WIDTH: self.pulse_width,
            AxisEnum.PULSE_INTERVAL_RANDOM: self.pulse_interval_random,
            AxisEnum.PULSE_RISE_TIME: self.pulse_rise_time,

            AxisEnum.VIBRATION_1_FREQUENCY: self.vibration_1_frequency,
            AxisEnum.VIBRATION_1_STRENGTH: self.vibration_1_strength,
            AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS: self.vibration_1_left_right_bias,
            AxisEnum.VIBRATION_1_HIGH_LOW_BIAS: self.vibration_1_high_low_bias,
            AxisEnum.VIBRATION_1_RANDOM: self.vibration_1_random,

            AxisEnum.VIBRATION_2_FREQUENCY: self.vibration_2_frequency,
            AxisEnum.VIBRATION_2_STRENGTH: self.vibration_2_strength,
            AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS: self.vibration_2_left_right_bias,
            AxisEnum.VIBRATION_2_HIGH_LOW_BIAS: self.vibration_2_high_low_bias,
            AxisEnum.VIBRATION_2_RANDOM: self.vibration_2_random,

            AxisEnum.INTENSITY_A: self.intensity_a,
            AxisEnum.INTENSITY_B: self.intensity_b,
            AxisEnum.INTENSITY_C: self.intensity_c,
            AxisEnum.INTENSITY_D: self.intensity_d,
        }

        kit = FunscriptKitModel.load_from_settings()
        mapping = {}
        for child in kit.children:
            child: FunscriptKitItem
            if len(child.tcode_axis_name) == 2:
                if child.axis in axis_enum_to_axis:
                    route = Route(axis_enum_to_axis[child.axis], child.limit_min, child.limit_max)
                    if child.tcode_axis_name not in mapping:
                        mapping[child.tcode_axis_name] = route
            elif len(child.tcode_axis_name) != 0:
                logger.error(f'Invalid T-Code axis name: {child.tcode_axis_name}. Axis name must be 2 chars.')

        self.mapping = mapping

    def set_carrier_axis(self, carrier: AbstractAxis):
        self.carrier_frequency = carrier
        self.reload_kit()

    def route_command(self, cmd: TCodeCommand):
        try:
            route = self.mapping[cmd.axis_identifier]
            route.axis.add(route.remap(cmd.value), cmd.interval / 1000.0)
            self.axis_updated.emit(route.axis)
            # Bridge: when alpha or beta is updated via TCode, also compute
            # and write 4-phase electrode intensities (e1-e4).
            # This is pointwise math with zero latency.
            if route.axis is self.alpha or route.axis is self.beta:
                self._bridge_alpha_beta_to_fourphase(cmd.interval / 1000.0)
        except KeyError:
            pass

    def _bridge_alpha_beta_to_fourphase(self, interval: float):
        """Convert current alpha/beta values to 4-phase electrode intensities.

        Uses the same transform chain as algorithm_factory's fourphase fallback:
        half_angle_to_full(a, b) → abc_to_e1234(a, b, c)

        Gamma (c) is derived in real-time based on the fourphase_gamma_mode setting:
        - 'speed': causal speed estimate from alpha/beta changes (running max normalization)
        - 'cycle': time-based sinusoidal oscillation (0.25 Hz)
        - 'position': bell-curve on alpha/beta radius (midrange = peak gamma)
        - otherwise: gamma = 0 (planar)

        After the tetrahedral transform, per-electrode response curves are applied
        based on the fourphase_electrode_curves setting.
        """
        from qt_ui import settings

        a = self.alpha.last_value()
        b = self.beta.last_value()

        # Compute gamma
        c = self._compute_realtime_gamma(a, b)

        # Wrap in 1-element arrays for the numpy transforms
        a_arr = np.array([a])
        b_arr = np.array([b])
        a_full, b_full = half_angle_to_full(a_arr, b_arr)
        c_arr = np.array([c])
        e = abc_to_e1234(a_full, b_full, c_arr)  # shape (4, 1)

        e1, e2, e3, e4 = e[0], e[1], e[2], e[3]

        # Apply per-electrode response curves
        curve_pack = settings.fourphase_electrode_curves.get()
        e1, e2, e3, e4 = apply_electrode_curves(e1, e2, e3, e4, curve_pack)

        e1, e2, e3, e4 = float(e1[0]), float(e2[0]), float(e3[0]), float(e4[0])

        self.intensity_a.add(e1, interval)
        self.intensity_b.add(e2, interval)
        self.intensity_c.add(e3, interval)
        self.intensity_d.add(e4, interval)

        # Emit updates so UI (bar chart, tetrahedron) refreshes
        self.axis_updated.emit(self.intensity_a)
        self.axis_updated.emit(self.intensity_b)
        self.axis_updated.emit(self.intensity_c)
        self.axis_updated.emit(self.intensity_d)

    def _compute_realtime_gamma(self, a: float, b: float) -> float:
        """Compute gamma value for the current alpha/beta in real-time.

        Reads fourphase_gamma_mode setting each call (cheap string comparison).
        """
        from qt_ui import settings
        mode = settings.fourphase_gamma_mode.get()

        now = time.monotonic()

        if mode == 'position':
            # Bell-curve on radius: gamma peaks at midrange, zero at rest/extremes
            c = float(position_based_gamma(np.array([a]), np.array([b]))[0])
            self._prev_alpha = a
            self._prev_beta = b
            self._prev_time = now
            return c

        if mode == 'cycle':
            # Sinusoidal oscillation at 0.25 Hz, scaled by current alpha/beta radius
            # Matches algorithm_factory._get_gamma_values cycle mode
            r = math.sqrt(a * a + b * b)
            c = math.sin(2 * math.pi * 0.25 * now) * max(r, 0.1)
            self._prev_alpha = a
            self._prev_beta = b
            self._prev_time = now
            return c

        if mode == 'speed':
            # Causal speed: |delta(a,b)| / dt, normalized by running max
            dt = now - self._prev_time
            if dt < 1e-6:
                dt = 1e-6
            da = a - self._prev_alpha
            db = b - self._prev_beta
            speed = math.sqrt(da * da + db * db) / dt

            # Update running max with slow decay so it adapts over time
            self._running_max_speed *= self._speed_decay
            if speed > self._running_max_speed:
                self._running_max_speed = speed
            # Ensure minimum to avoid division by zero
            max_spd = max(self._running_max_speed, 1e-6)
            normalized_speed = min(speed / max_spd, 1.0)

            # Scale by alpha/beta radius (matches precomputed version)
            r = math.sqrt(a * a + b * b)
            c = normalized_speed * max(r, 0.1)

            self._prev_alpha = a
            self._prev_beta = b
            self._prev_time = now
            return c

        # Default: planar (gamma = 0)
        self._prev_alpha = a
        self._prev_beta = b
        self._prev_time = now
        return 0.0
