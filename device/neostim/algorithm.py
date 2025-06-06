import struct
import time

from PyQt5.QtCore import QObject, QTimer

import numpy as np

import stim_math
from device.neostim.neostim_device import NeoStimPTGenerator, AttributeId, Encoding, RestimPulseParameters
from device.neostim.neostim_device import NeoStim

import device.neostim.threephase
from device.neostim import limits

from stim_math.audio_gen.params import NeoStimParams, NeoStimDebugParams
from stim_math.audio_gen.various import ThreePhasePosition
from stim_math.axis import AbstractMediaSync


class NeoStimAlgorithm(QObject, NeoStimPTGenerator):
    def __init__(self, media: AbstractMediaSync, params: NeoStimParams):
        super().__init__()
        self.media = media
        self.params = params
        self.position_params = ThreePhasePosition(params.position, params.transform)

        self.params = params
        self.device: NeoStim = None
        self.device_ready = False

        self.params_update_timer = QTimer()
        self.params_update_timer.timeout.connect(self.update_params)
        self.params_update_timer.setInterval(50)

        self.set_intensity = None

        self.pulse_planner = device.neostim.threephase.ThreePhasePlanner()

    def link_device(self, device: NeoStim):
        self.device = device

    def device_connected_and_ready(self):
        assert self.device_ready == False
        self.device_ready = True

        self.update_params()
        self.device.start_restim()
        self.params_update_timer.start()

    def device_about_to_disconnect(self):
        self.device.stop_restim()
        self.device_ready = False
        self.params_update_timer.stop()

    def update_params(self):
        t = time.time()

        # set device voltage
        voltage = self.params.voltage.last_value()
        intensity = np.clip(int(voltage / .080), 0, 255)  # 80mv
        if self.set_intensity != intensity:
            self.set_intensity = intensity;
            self.device.send_attr_write_request(AttributeId.IntensityPercent,
                                                struct.pack(b'BB', Encoding.UnsignedInt1.value, intensity))

        # collect pulse parameters
        volume = \
            np.clip(self.params.volume.master.last_value(), 0, 1) * \
            np.clip(self.params.volume.api.interpolate(t), 0, 1) * \
            np.clip(self.params.volume.inactivity.last_value(), 0, 1) * \
            np.clip(self.params.volume.external.last_value(), 0, 1)

        alpha, beta = self.position_params.get_position(t)
        calibration_neutral = self.params.calibrate.neutral.last_value()
        calibration_right = self.params.calibrate.right.last_value()
        calibration_center = self.params.calibrate.center.last_value()

        center_calib = stim_math.threephase.ThreePhaseCenterCalibration(calibration_center)
        volume *= center_calib.get_scale(alpha, beta)

        pulse_freq = self.params.pulse_frequency.interpolate(t)
        pulse_freq = np.clip(pulse_freq, limits.PulseFrequency.min, limits.PulseFrequency.max)

        carrier_frequency = np.clip(self.params.carrier_frequency.interpolate(t), limits.CarrierFrequency.min,
                                    limits.CarrierFrequency.max)
        pulse_width = int(500000.0 / carrier_frequency)
        duty_cycle_at_max_power = np.clip(self.params.duty_cycle_at_max_power.last_value(), limits.DutyCycle.min, limits.DutyCycle.max)
        inversion_time = self.params.inversion_time.interpolate(t)
        switch_time = self.params.switch_time.interpolate(t)
        debug: NeoStimDebugParams = self.params.debug.last_value()

        self.pulse_planner.set_debug_options(debug)
        a_strength, b_strength, ab_strength, ac_strength, bc_strength = self.pulse_planner.compute_bounds(
            alpha, beta, volume,
            calibration_neutral, calibration_right, calibration_center
        )

        params = RestimPulseParameters(
            int(a_strength * 1024),
            int(b_strength * 1024),
            0,
            0,
            int(ab_strength * 1024),
            int(bc_strength * 1024),
            0,
            int(ac_strength * 1024),
            int(duty_cycle_at_max_power * 1024),
            int(pulse_width),
            int(inversion_time),
            int(switch_time),
            int(1e6 / pulse_freq),
            0,
            int(debug.defeat_randomization)
        )
        # print(params)
        self.device.queue_restim_parameters(params)

