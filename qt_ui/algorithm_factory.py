from __future__ import annotations  # multiple return values
import logging
import numpy as np

from device.focstim.fourphase_algorithm import FOCStimFourphaseAlgorithm
from device.neostim.algorithm import NeoStimAlgorithm
from qt_ui.device_wizard.enums import DeviceConfiguration, DeviceType, WaveformType
from stim_math.audio_gen.base_classes import AudioGenerationAlgorithm
from device.focstim.threephase_algorithm import FOCStimThreephaseAlgorithm
from stim_math.audio_gen.pulse_based import DefaultThreePhasePulseBasedAlgorithm, ABTestThreePhasePulseBasedAlgorithm
from stim_math.audio_gen.continuous import ThreePhaseAlgorithm
from stim_math.audio_gen.params import *

from qt_ui.models.funscript_kit import FunscriptKitModel
from qt_ui.models.script_mapping import ScriptMappingModel
from qt_ui.device_wizard.axes import AxisEnum
from stim_math.axis import create_precomputed_axis, AbstractTimestampMapper, create_constant_axis, AbstractMediaSync

logger = logging.getLogger('restim.algorithm_factory')


class AlgorithmFactory:
    def __init__(self, mainwindow,
                 kit: FunscriptKitModel,
                 script_mapping: ScriptMappingModel,
                 timestamp_mapper: AbstractTimestampMapper,
                 media_sync: AbstractMediaSync,
                 load_funscripts: bool = True,
                 create_for_bake: bool = False,
                 ):
        # TODO: not very nice to reference mainwindow...
        self.mainwindow = mainwindow
        self.kit = kit
        self.script_mapping = script_mapping
        self.timestamp_mapper = timestamp_mapper
        self.media_sync = media_sync
        self.load_funscripts = load_funscripts
        self.create_for_bake = create_for_bake
        self._fourphase_fallback_cache = None  # lazy-computed (e1, e2, e3, e4) axes
        self._threephase_fallback_cache = None  # lazy-computed (alpha, beta) axes from 1D funscript
        self._pulse_auto_derive_cache = None  # lazy-computed pulse param axes

    def create_algorithm(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm | NeoStimAlgorithm:
        if device.device_type == DeviceType.AUDIO_THREE_PHASE:
            if device.waveform_type == WaveformType.CONTINUOUS:
                return self.create_3phase_continuous(device)
            elif device.waveform_type == WaveformType.PULSE_BASED:
                return self.create_3phase_pulsebased(device)
            elif device.waveform_type == WaveformType.A_B_TESTING:
                return self.create_3phase_abtest(device)
            else:
                raise RuntimeError('unknown waveform type')
        elif device.device_type == DeviceType.FOCSTIM_THREE_PHASE:
            return self.create_focstim_3phase_pulsebased(device)
        elif device.device_type == DeviceType.FOCSTIM_FOUR_PHASE:
            return self.create_focstim_4phase_pulsebased(device)
        elif device.device_type == DeviceType.NEOSTIM_THREE_PHASE:
            return self.create_neostim(device)
        else:
            raise RuntimeError('unknown device type')

    def create_3phase_continuous(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = ThreePhaseAlgorithm(
            self.media_sync,
            ThreephaseContinuousAlgorithmParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                carrier_frequency=self.get_axis_continuous_carrier_frequency(),
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def create_3phase_pulsebased(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = DefaultThreePhasePulseBasedAlgorithm(
            self.media_sync,
            ThreephasePulsebasedAlgorithmParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                carrier_frequency=self.get_axis_pulse_carrier_frequency(),
                pulse_frequency=self.get_axis_pulse_frequency(),
                pulse_width=self.get_axis_pulse_width(),
                pulse_interval_random=self.get_axis_pulse_interval_random(),
                pulse_rise_time=self.get_axis_pulse_rise_time(),
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            )
        )
        return algorithm

    def create_3phase_abtest(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = ABTestThreePhasePulseBasedAlgorithm(
            self.media_sync,
            ThreephaseABTestAlgorithmParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                vibration_1=self.get_axis_vib1_all(),
                vibration_2=self.get_axis_vib2_all(),
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                a_volume=self.mainwindow.tab_a_b_testing.axis_a_volume,
                a_train_duration=self.mainwindow.tab_a_b_testing.axis_a_train_duration,
                a_carrier_frequency=self.mainwindow.tab_a_b_testing.axis_a_carrier_frequency,
                a_pulse_frequency=self.mainwindow.tab_a_b_testing.axis_a_pulse_frequency,
                a_pulse_width=self.mainwindow.tab_a_b_testing.axis_a_pulse_width,
                a_pulse_interval_random=self.mainwindow.tab_a_b_testing.axis_a_pulse_interval_random,
                a_pulse_rise_time=self.mainwindow.tab_a_b_testing.axis_a_pulse_rise_time,
                b_volume=self.mainwindow.tab_a_b_testing.axis_b_volume,
                b_train_duration=self.mainwindow.tab_a_b_testing.axis_b_train_duration,
                b_carrier_frequency=self.mainwindow.tab_a_b_testing.axis_b_carrier_frequency,
                b_pulse_frequency=self.mainwindow.tab_a_b_testing.axis_b_pulse_frequency,
                b_pulse_width=self.mainwindow.tab_a_b_testing.axis_b_pulse_width,
                b_pulse_interval_random=self.mainwindow.tab_a_b_testing.axis_b_pulse_interval_random,
                b_pulse_rise_time=self.mainwindow.tab_a_b_testing.axis_b_pulse_rise_time,
            ),
            safety_limits=SafetyParams(
                device.min_frequency,
                device.max_frequency,
            ),
            waveform_change_callback=self.mainwindow.tab_a_b_testing.test_waveform_changed,
        )
        return algorithm

    def create_focstim_3phase_pulsebased(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = FOCStimThreephaseAlgorithm(
            self.media_sync,
            FOCStimParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                carrier_frequency=self.get_axis_pulse_carrier_frequency(),
                pulse_frequency=self.get_axis_pulse_frequency(),
                pulse_width=self.get_axis_pulse_width(),
                pulse_interval_random=self.get_axis_pulse_interval_random(),
                pulse_rise_time=self.get_axis_pulse_rise_time(),
                tau=self.get_axis_tau(),
            ),
            safety_limits=SafetyParamsFOC(
                device.min_frequency,
                device.max_frequency,
                device.waveform_amplitude_amps,
            )
        )
        return algorithm

    def create_focstim_4phase_pulsebased(self, device: DeviceConfiguration) -> AudioGenerationAlgorithm:
        algorithm = FOCStimFourphaseAlgorithm(
            self.media_sync,
            FourphaseFOCStimParams(
                position=FourphaseIntensityParams(
                    self.get_axis_intensity_a(),
                    self.get_axis_intensity_b(),
                    self.get_axis_intensity_c(),
                    self.get_axis_intensity_d(),
                ),
                # transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_fourphase.calibrate_params,
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                carrier_frequency=self.get_axis_pulse_carrier_frequency(),
                pulse_frequency=self.get_axis_pulse_frequency(),
                pulse_width=self.get_axis_pulse_width(),
                pulse_interval_random=self.get_axis_pulse_interval_random(),
                pulse_rise_time=self.get_axis_pulse_rise_time(),
                tau=self.get_axis_tau(),
            ),
            safety_limits=SafetyParamsFOC(
                device.min_frequency,
                device.max_frequency,
                device.waveform_amplitude_amps,
            )
        )
        return algorithm

    def create_neostim(self, device: DeviceConfiguration) -> NeoStimAlgorithm:
        algorithm = NeoStimAlgorithm(
            self.media_sync,
            NeoStimParams(
                position=ThreephasePositionParams(
                    self.get_axis_alpha(),
                    self.get_axis_beta(),
                ),
                transform=self.mainwindow.tab_threephase.transform_params,
                calibrate=self.mainwindow.tab_threephase.calibrate_params,
                volume=VolumeParams(
                    api=self.get_axis_volume_api(),
                    master=self.get_axis_volume_master(),
                    inactivity=self.get_axis_volume_inactivity(),
                    external=self.get_axis_volume_external(),
                ),
                voltage=self.get_axis_neostim_voltage(),
                pulse_frequency=self.get_axis_neostim_pulse_frequency(),
                duty_cycle_at_max_power=self.get_axis_neostim_duty_cycle_at_max_power(),
                carrier_frequency=self.get_axis_neostim_carrier_frequency(),
                inversion_time=self.get_axis_neostim_inversion_time(),
                switch_time=self.get_axis_neostim_switch_time(),
                debug=self.get_axis_neostim_debug(),
            ),
        )
        return algorithm

    def get_axis_alpha(self):
        return self.get_axis_from_script_mapping(AxisEnum.POSITION_ALPHA) or self._get_threephase_fallback('alpha') or self.mainwindow.alpha

    def get_axis_beta(self):
        return self.get_axis_from_script_mapping(AxisEnum.POSITION_BETA) or self._get_threephase_fallback('beta') or self.mainwindow.beta

    def get_axis_gamma(self):
        return self.get_axis_from_script_mapping(AxisEnum.POSITION_GAMMA) or self.mainwindow.gamma

    def get_axis_intensity_a(self):
        return self.get_axis_from_script_mapping(AxisEnum.INTENSITY_A) or self._get_fourphase_fallback(0) or self.mainwindow.intensity_a

    def get_axis_intensity_b(self):
        return self.get_axis_from_script_mapping(AxisEnum.INTENSITY_B) or self._get_fourphase_fallback(1) or self.mainwindow.intensity_b

    def get_axis_intensity_c(self):
        return self.get_axis_from_script_mapping(AxisEnum.INTENSITY_C) or self._get_fourphase_fallback(2) or self.mainwindow.intensity_c

    def get_axis_intensity_d(self):
        return self.get_axis_from_script_mapping(AxisEnum.INTENSITY_D) or self._get_fourphase_fallback(3) or self.mainwindow.intensity_d

    def _get_threephase_fallback(self, component: str):
        """Return a precomputed alpha or beta axis by auto-converting a bare 1D funscript.

        Only activates when no explicit alpha/beta funscripts are loaded but a bare 1D
        funscript is available.

        component: 'alpha' or 'beta'
        """
        if self._threephase_fallback_cache is None:
            self._threephase_fallback_cache = self._compute_threephase_fallback()
        if self._threephase_fallback_cache:
            return self._threephase_fallback_cache.get(component)
        return None

    def _compute_threephase_fallback(self):
        """Try to auto-convert a bare 1D funscript to alpha/beta for 3-phase devices.

        Only fires when:
        - No explicit alpha funscript is loaded
        - No explicit beta funscript is loaded
        - A bare 1D funscript IS loaded
        """
        if not self.load_funscripts:
            return None

        # Don't activate if alpha or beta are already explicitly mapped
        alpha_item = self.script_mapping.get_config_for_axis(AxisEnum.POSITION_ALPHA)
        beta_item = self.script_mapping.get_config_for_axis(AxisEnum.POSITION_BETA)
        if (alpha_item and alpha_item.script is not None) or (beta_item and beta_item.script is not None):
            return None

        bare_funscript = self._find_bare_funscript()
        if bare_funscript is None or bare_funscript.script is None:
            return None

        from funscript.funscript_conversion import convert_1d_to_2d
        from qt_ui import settings
        prob = settings.funscript_conversion_random_direction_change_probability.get()
        logger.info(f'Auto-converting 1D funscript to 3-phase alpha/beta '
                    f'(random_direction_change_probability={prob:.2f})')
        t, alpha, beta = convert_1d_to_2d(bare_funscript.script, prob)
        timestamps = np.array(t)

        alpha_lim_min, alpha_lim_max = self.kit.limits_for_axis(AxisEnum.POSITION_ALPHA)
        beta_lim_min, beta_lim_max = self.kit.limits_for_axis(AxisEnum.POSITION_BETA)
        alpha_values = np.clip(alpha, 0, 1) * (alpha_lim_max - alpha_lim_min) + alpha_lim_min
        beta_values = np.clip(beta, 0, 1) * (beta_lim_max - beta_lim_min) + beta_lim_min

        return {
            'alpha': create_precomputed_axis(timestamps, alpha_values, self.timestamp_mapper),
            'beta': create_precomputed_axis(timestamps, beta_values, self.timestamp_mapper),
        }

    def _get_fourphase_fallback(self, index: int):
        """Return a precomputed electrode axis by auto-converting from alpha/beta or 1D funscripts.

        Conversion priority:
        1. alpha + beta funscripts loaded → convert to 4 electrode intensities
        2. bare 1D funscript (no suffix) loaded → convert 1D→2D→4 electrode intensities
        3. None (no fallback available)
        """
        if self._fourphase_fallback_cache is None:
            self._fourphase_fallback_cache = self._compute_fourphase_fallback()
        if self._fourphase_fallback_cache:
            return self._fourphase_fallback_cache[index]
        return None

    def _compute_fourphase_fallback(self):
        """Try to auto-convert available funscripts to 4-phase electrode intensities."""
        import stim_math.transforms
        import stim_math.transforms_4

        if not self.load_funscripts:
            return None

        # Priority 1: alpha + beta funscripts → 4-phase
        alpha_item = self.script_mapping.get_config_for_axis(AxisEnum.POSITION_ALPHA)
        beta_item = self.script_mapping.get_config_for_axis(AxisEnum.POSITION_BETA)
        if alpha_item and beta_item and alpha_item.script is not None and beta_item.script is not None:
            logger.info('Auto-converting alpha/beta funscripts to 4-phase electrode intensities')
            timestamps = np.union1d(alpha_item.script.x, beta_item.script.x)
            alpha_lim_min, alpha_lim_max = self.kit.limits_for_axis(AxisEnum.POSITION_ALPHA)
            beta_lim_min, beta_lim_max = self.kit.limits_for_axis(AxisEnum.POSITION_BETA)
            a = np.interp(timestamps, alpha_item.script.x,
                          np.clip(alpha_item.script.y, 0, 1) * (alpha_lim_max - alpha_lim_min) + alpha_lim_min)
            b = np.interp(timestamps, beta_item.script.x,
                          np.clip(beta_item.script.y, 0, 1) * (beta_lim_max - beta_lim_min) + beta_lim_min)
            a, b = stim_math.transforms.half_angle_to_full(a, b)
            e1, e2, e3, e4 = stim_math.transforms_4.abc_to_e1234(a, b, np.zeros_like(a))
            return self._make_fourphase_axes(timestamps, e1, e2, e3, e4)

        # Priority 2: bare 1D funscript → 1D→2D→4-phase
        bare_funscript = self._find_bare_funscript()
        if bare_funscript and bare_funscript.script is not None:
            from funscript.funscript_conversion import convert_1d_to_2d
            from qt_ui import settings
            prob = settings.funscript_conversion_random_direction_change_probability.get()
            logger.info(f'Auto-converting 1D funscript to 4-phase electrode intensities '
                        f'(random_direction_change_probability={prob:.2f})')
            t, alpha, beta = convert_1d_to_2d(bare_funscript.script, prob)
            timestamps = np.array(t)
            a = np.array(alpha) * 2 - 1
            b = np.array(beta) * 2 - 1
            a, b = stim_math.transforms.half_angle_to_full(a, b)
            e1, e2, e3, e4 = stim_math.transforms_4.abc_to_e1234(a, b, np.zeros_like(a))
            return self._make_fourphase_axes(timestamps, e1, e2, e3, e4)

        return None

    def _find_bare_funscript(self):
        """Find a funscript with no suffix (bare 1D stroke data) in the script mapping."""
        from qt_ui.models.script_mapping import FunscriptTreeItem
        for item in self.script_mapping.funscript_conifg():
            if isinstance(item, FunscriptTreeItem) and item.funscript_type == '' and not item.has_broken_script():
                return item
        return None

    def _make_fourphase_axes(self, timestamps, e1, e2, e3, e4):
        """Create 4 precomputed axes from electrode intensity arrays."""
        return (
            create_precomputed_axis(timestamps, np.clip(e1, 0, 1), self.timestamp_mapper),
            create_precomputed_axis(timestamps, np.clip(e2, 0, 1), self.timestamp_mapper),
            create_precomputed_axis(timestamps, np.clip(e3, 0, 1), self.timestamp_mapper),
            create_precomputed_axis(timestamps, np.clip(e4, 0, 1), self.timestamp_mapper),
        )

    def _get_pulse_auto_derive(self, param_name: str):
        """Return a precomputed axis for a pulse parameter auto-derived from motion data.

        Only active when pulse_auto_derive is enabled in settings and no explicit
        funscript is loaded for the requested parameter.

        param_name: one of 'pulse_frequency', 'carrier_frequency', 'pulse_width', 'pulse_rise_time'
        """
        from qt_ui import settings as s
        if not s.pulse_auto_derive_enabled.get():
            return None

        if self._pulse_auto_derive_cache is None:
            self._pulse_auto_derive_cache = self._compute_pulse_auto_derive()
        if self._pulse_auto_derive_cache and param_name in self._pulse_auto_derive_cache:
            return self._pulse_auto_derive_cache[param_name]
        return None

    def _compute_pulse_auto_derive(self):
        """Compute auto-derived pulse parameters from the loaded motion funscripts.

        Uses the same motion data as the fourphase fallback:
        1. alpha + beta → use alpha as the modulation source, main = alpha
        2. bare 1D → use raw stroke data as main, 2D-converted alpha as alpha
        3. None → no auto-derivation possible
        """
        from qt_ui.pulse_auto_derive import PulseAutoDeriver

        if not self.load_funscripts:
            return None

        deriver = PulseAutoDeriver()
        main_t = main_p = alpha_t = alpha_p = None

        # Priority 1: bare 1D funscript → best source for speed
        bare_funscript = self._find_bare_funscript()
        if bare_funscript and bare_funscript.script is not None:
            main_t = bare_funscript.script.x
            main_p = bare_funscript.script.y
            # Also look for alpha
            alpha_item = self.script_mapping.get_config_for_axis(AxisEnum.POSITION_ALPHA)
            if alpha_item and alpha_item.script is not None:
                alpha_t = alpha_item.script.x
                alpha_p = alpha_item.script.y
            logger.info('Auto-deriving pulse parameters from 1D funscript')

        # Priority 2: alpha funscript → use alpha as both main and alpha
        if main_t is None:
            alpha_item = self.script_mapping.get_config_for_axis(AxisEnum.POSITION_ALPHA)
            if alpha_item and alpha_item.script is not None:
                main_t = alpha_item.script.x
                main_p = alpha_item.script.y
                alpha_t = alpha_item.script.x
                alpha_p = alpha_item.script.y
                logger.info('Auto-deriving pulse parameters from alpha funscript')

        if main_t is None:
            logger.debug('No funscript available for pulse auto-derivation')
            return None

        try:
            results = deriver.derive_all(main_t, main_p, alpha_t, alpha_p)
        except Exception as e:
            logger.warning(f'Failed to auto-derive pulse parameters: {e}')
            return None

        # Convert results to precomputed axes
        axes = {}
        for param_name, (timestamps, values) in results.items():
            axes[param_name] = create_precomputed_axis(
                timestamps, values, self.timestamp_mapper
            )

        return axes

    def get_axis_volume_api(self):
        return self.get_axis_from_script_mapping(AxisEnum.VOLUME_API) or self.mainwindow.tab_volume.axis_api_volume

    def get_axis_volume_master(self):
        if self.create_for_bake:
            return create_constant_axis(1.0)    # ramp does NOT work in bake mode
        return self.mainwindow.tab_volume.axis_master_volume

    def get_axis_volume_inactivity(self):
        if self.create_for_bake:
            return create_constant_axis(1.0)    # inactivity does NOT work in bake mode
        return self.mainwindow.tab_volume.axis_inactivity_volume

    def get_axis_volume_external(self):
        if self.create_for_bake:
            return create_constant_axis(1.0)    # external volume does NOT work in bake mode
        return self.mainwindow.tab_volume.axis_external_volume

    def get_axis_tau(self):
        return self.mainwindow.tab_volume.axis_tau

    def get_axis_continuous_carrier_frequency(self):
        default = self.mainwindow.tab_carrier.axis_carrier
        return self.get_axis_from_script_mapping(AxisEnum.CARRIER_FREQUENCY) or default

    def get_axis_pulse_carrier_frequency(self):
        default = self.mainwindow.tab_pulse_settings.axis_carrier_frequency
        return self.get_axis_from_script_mapping(AxisEnum.CARRIER_FREQUENCY) or \
               self._get_pulse_auto_derive('carrier_frequency') or default

    def get_axis_pulse_frequency(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_FREQUENCY) or \
               self._get_pulse_auto_derive('pulse_frequency') or \
               self.mainwindow.tab_pulse_settings.axis_pulse_frequency

    def get_axis_pulse_width(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_WIDTH) or \
               self._get_pulse_auto_derive('pulse_width') or \
               self.mainwindow.tab_pulse_settings.axis_pulse_width

    def get_axis_pulse_interval_random(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_INTERVAL_RANDOM) or \
               self.mainwindow.tab_pulse_settings.axis_pulse_interval_random

    def get_axis_pulse_rise_time(self):
        return self.get_axis_from_script_mapping(AxisEnum.PULSE_RISE_TIME) or \
            self._get_pulse_auto_derive('pulse_rise_time') or \
            self.mainwindow.tab_pulse_settings.axis_pulse_rise_time

    def get_axis_vib1_all(self):
        return VibrationParams(
            enabled=self.get_axis_vib1_enabled(),
            frequency=self.get_axis_vib1_frequency(),
            strength=self.get_axis_vib1_strength(),
            left_right_bias=self.get_axis_vib1_left_right_bias(),
            high_low_bias=self.get_axis_vib1_high_low_bias(),
            random=self.get_axis_vib1_random(),
        )

    def get_axis_vib1_enabled(self):
        is_enabled = \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_FREQUENCY) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_STRENGTH) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_HIGH_LOW_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_1_RANDOM)
        if is_enabled:
            return create_precomputed_axis([0], [True], self.timestamp_mapper)
        else:
            return self.mainwindow.tab_vibrate.vibration_1.enabled

    def get_axis_vib1_frequency(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_FREQUENCY) or \
               self.mainwindow.tab_vibrate.vibration_1.frequency

    def get_axis_vib1_strength(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_STRENGTH) or \
               self.mainwindow.tab_vibrate.vibration_1.strength

    def get_axis_vib1_left_right_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_1.left_right_bias

    def get_axis_vib1_high_low_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_HIGH_LOW_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_1.high_low_bias

    def get_axis_vib1_random(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_1_RANDOM) or \
               self.mainwindow.tab_vibrate.vibration_1.random

    def get_axis_vib2_all(self):
        return VibrationParams(
            enabled=self.get_axis_vib2_enabled(),
            frequency=self.get_axis_vib2_frequency(),
            strength=self.get_axis_vib2_strength(),
            left_right_bias=self.get_axis_vib2_left_right_bias(),
            high_low_bias=self.get_axis_vib2_high_low_bias(),
            random=self.get_axis_vib2_random(),
        )

    def get_axis_vib2_enabled(self):
        is_enabled = \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_FREQUENCY) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_STRENGTH) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_HIGH_LOW_BIAS) or \
            self.script_mapping.get_config_for_axis(AxisEnum.VIBRATION_2_RANDOM)
        if is_enabled:
            return create_precomputed_axis([0], [True], self.timestamp_mapper)
        else:
            return self.mainwindow.tab_vibrate.vibration_2.enabled

    def get_axis_vib2_frequency(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_FREQUENCY) or \
               self.mainwindow.tab_vibrate.vibration_2.frequency

    def get_axis_vib2_strength(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_STRENGTH) or \
               self.mainwindow.tab_vibrate.vibration_2.strength

    def get_axis_vib2_left_right_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_2.left_right_bias

    def get_axis_vib2_high_low_bias(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_HIGH_LOW_BIAS) or \
               self.mainwindow.tab_vibrate.vibration_2.high_low_bias

    def get_axis_vib2_random(self):
        return self.get_axis_from_script_mapping(AxisEnum.VIBRATION_2_RANDOM) or \
               self.mainwindow.tab_vibrate.vibration_2.random

    def get_axis_neostim_voltage(self):
        return self.mainwindow.tab_neostim.axis_voltage

    def get_axis_neostim_carrier_frequency(self):
        return self.mainwindow.tab_neostim.axis_carrier_frequency

    def get_axis_neostim_pulse_frequency(self):
        return self.mainwindow.tab_neostim.axis_pulse_frequency

    def get_axis_neostim_duty_cycle_at_max_power(self):
        return self.mainwindow.tab_neostim.axis_duty_cycle_at_max_power

    def get_axis_neostim_inversion_time(self):
        return self.mainwindow.tab_neostim.axis_inversion_time

    def get_axis_neostim_switch_time(self):
        return self.mainwindow.tab_neostim.axis_switch_time

    def get_axis_neostim_debug(self):
        return self.mainwindow.tab_neostim.axis_debug

    def get_axis_from_script_mapping(self, axis: AxisEnum) -> AbstractAxis | None:
        if not self.load_funscripts:
            return None

        funscript_item = self.script_mapping.get_config_for_axis(axis)
        if funscript_item:
            limit_min, limit_max = self.kit.limits_for_axis(axis)
            # TODO: not very memory efficient if multiple algorithms reference the same script.
            # but worst-case it only wastes a few MB or so...
            return create_precomputed_axis(funscript_item.script.x,
                                           np.clip(funscript_item.script.y, 0, 1) * (limit_max - limit_min) + limit_min,
                                           self.timestamp_mapper)
        else:
            return None
