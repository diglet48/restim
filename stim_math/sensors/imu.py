from dataclasses import dataclass

import numpy as np
import scipy

from ahrs import Quaternion
from ahrs.common.orientation import acc2q
from ahrs.filters import Madgwick

from net import teleplot

GRAVITY_MAGNITUDE = 9.80

@dataclass
class IMUData:
    samplerate: float
    acc_x: float    # acceleration in mili-g
    acc_y: float
    acc_z: float
    gyr_x: float    # angular rotation in mili-degrees-per-second
    gyr_y: float
    gyr_z: float


# TODO: optimize away scipy
class HighPass:
    def __init__(self, bandlimit, samplerate):
        self.sos = scipy.signal.butter(1, bandlimit, 'highpass', fs=samplerate, output='sos')
        self.zi = scipy.signal.sosfilt_zi(self.sos)
        self.zi *= 0

    def update(self, data):
        out, self.zi = scipy.signal.sosfilt(self.sos, [data], zi=self.zi)
        return out[0]


class IMUAlgorithm:
    def __init__(self,
                 axis_movement_fullscale, axis_movement_out,
                 axis_velocity_fullscale, axis_intensity_increase,
                 samplerate):

        self.axis_movement_fullscale = axis_movement_fullscale
        self.axis_movement_out = axis_movement_out
        self.axis_velocity_fullscale = axis_velocity_fullscale
        self.axis_intensity_increase = axis_intensity_increase

        self.q = None
        self.orientation_filter = Madgwick(frequency=samplerate)
        self.velocity = np.zeros(3, dtype=np.float64)
        self.position = np.zeros(3, dtype=np.float64)

        bandlimit = 0.5
        self.acc_filter_x = HighPass(bandlimit, samplerate=samplerate)
        self.acc_filter_y = HighPass(bandlimit, samplerate=samplerate)
        self.acc_filter_z = HighPass(bandlimit, samplerate=samplerate)
        bandlimit = 0.5
        self.velocity_filter_x = HighPass(bandlimit, samplerate=samplerate)
        self.velocity_filter_y = HighPass(bandlimit, samplerate=samplerate)
        self.velocity_filter_z = HighPass(bandlimit, samplerate=samplerate)
        bandlimit = 0.5
        self.position_filter_x = HighPass(bandlimit, samplerate=samplerate)
        self.position_filter_y = HighPass(bandlimit, samplerate=samplerate)
        self.position_filter_z = HighPass(bandlimit, samplerate=samplerate)

        self.forward_vector = np.array([0, 0, 1], dtype=np.float64)

        self.forward_velocity = 0
        self.forward_position = 0

    # TODO: implement if needed
    def set_calibration(self):
        pass

    def last_position(self):
        return self.forward_position

    def last_velocity(self):
        return self.forward_velocity

    def update(self, data: IMUData):
        gyr = np.array([data.gyr_x, data.gyr_y, data.gyr_z], dtype=np.float64)
        acc = np.array([data.acc_x, data.acc_y, data.acc_z], dtype=np.float64)

        # calibration for my device.
        # TODO: make calibration configurable
        gyr_offset = np.array([426.68551375, -846.5071164, 365.27666212])
        gyr = gyr - gyr_offset
        acc_offsets = np.array([-11.26820513, -19.80804002, 12.53697226])
        acc_matrix = np.array([[9.88870903e-01, 0.00000000e+00, 0.00000000e+00],
                               [8.66923473e-04, 1.00103198e+00, 0.00000000e+00],
                               [-7.18050029e-03, -1.13429312e-03, 1.00070187e+00]])
        acc = (acc_matrix @ (acc - acc_offsets).T).T


        mdps_to_rads = 1 / 360 / 1000 * (2 * np.pi)
        gyr = gyr * mdps_to_rads
        acc = acc / 1000 * GRAVITY_MAGNITUDE
        dt = 1 / data.samplerate

        # initial conditions
        if self.q is None:
            self.q = acc2q(acc)
        self.q = self.orientation_filter.updateIMU(self.q, gyr, acc, dt=dt)

        acc_without_gravity = Quaternion(self.q).rotate(acc) - [0, 0, GRAVITY_MAGNITUDE]
        acc_without_gravity_f = np.array([
            self.acc_filter_x.update(acc_without_gravity[0]),
            self.acc_filter_y.update(acc_without_gravity[1]),
            self.acc_filter_z.update(acc_without_gravity[2]),
        ])
        self.velocity += acc_without_gravity_f * dt
        velocity_f = np.array([
            self.velocity_filter_x.update(self.velocity[0]),
            self.velocity_filter_y.update(self.velocity[1]),
            self.velocity_filter_z.update(self.velocity[2]),
        ])
        self.position += velocity_f * dt
        position_f = np.array([
            self.position_filter_x.update(self.position[0]),
            self.position_filter_y.update(self.position[1]),
            self.position_filter_z.update(self.position[2]),
        ])

        if self.forward_vector is None:
            self.forward_vector = Quaternion(self.q).rotate(np.array([0, 0, -1]))
        else:
            self.forward_vector += 0.01 * (self.forward_vector - Quaternion(self.q).rotate(np.array([0, 0, -1])))
            self.forward_vector /= np.linalg.norm(self.forward_vector)

        self.forward_velocity = np.dot(velocity_f, self.forward_vector)
        self.forward_position = np.dot(position_f, self.forward_vector)

        tp = teleplot.Teleplot()
        tp.write_metrics(
            f_v=self.forward_velocity,
            f_p=self.forward_position,
        )

    def transform_threephase(self, volume: float, alpha: float, beta: float):
        movement_amplitude_in = self.axis_movement_fullscale.last_value() / 100   # meters
        movement_amplitude_out = self.axis_movement_out.last_value()

        if movement_amplitude_in != 0 and movement_amplitude_out != 0:
            alpha += np.clip(self.forward_position / movement_amplitude_in, -1, 1) * movement_amplitude_out

            # clip alpha, beta to unit circle
            r = (alpha**2 + beta**2)**.5
            if r > 1:
                alpha /= r
                beta /= r

        velocity_amplitude_in = self.axis_velocity_fullscale.last_value() / 100   # m/s
        velocity_amplitude_out = np.clip(self.axis_intensity_increase.last_value(), -1, 1)

        if velocity_amplitude_in and velocity_amplitude_out and volume:
            s = np.clip(np.abs(self.forward_velocity / velocity_amplitude_in), 0, 1)
            if velocity_amplitude_out >= 0:
                # increase with speed
                volume *= 1 - velocity_amplitude_out * (1 - s)
            else:
                # decrease with speed
                volume *= 1 + velocity_amplitude_out * s

        return volume, alpha, beta

