import numpy as np

class EOMController:
    """
    Implementation of the edging algorithm as in the Edge-o-Matic 3000

    The algorithm keeps track of an arousal variable. This variable
    decays quickly (time constant 500ms, hardcoded in EOM), and
    can be interpreted as the accumulation of recent clenches.

    Whenever an increase in pressure is detected, it is simply added
    to the arousal value. Therefore, the unit of arousal is pascal.

    When the arousal is above the static threshold, it is considered
    an edge and toy speed backs off to the minimum.

    On the EOM, pressure is a direct reading from the ADC (4096),
    I'm guessing the default settings are designed for a full
    range of about 8kPa.

    On the EOM, it is recommended to only inflate the plug slightly.
    This is a hardware/software issue with the EOM, the sparkfun
    micropressure sensor has no such issues. Because of physics,
    the same arousal threshold works for all inflation levels.

    This class also implements the depletion-mode controller.
    The toy speed starts at the minimum and ramps to the maximum
    (default: 30s). The toy speed is further reduced by a factor of
    (arousal / arousal_threshold).

    The EOM also implements clench detection to further increase
    the arousal value. Searching discord did not turn up any
    references of people using this. Furthermore, the clench detection
    only slightly increases the arousal for a very short time, not
    enough to trigger an edge by itself. I choose to omit this.
    """
    def __init__(self):
        self.arousal = 0
        self.arousal_time_constant = np.log(.99) * 50  # EOM: multiply by 0.99 at 50hz

        # EOM setting: sensitivity_threshold
        # On the EOM, the default is around 1.2 kPa. A full clench
        # ranges 3-4 kPa, so it backs off on relatively small clenches.
        self.arousal_threshold = 1300   # pascal

        # On the EOM, this is hardcoded to sensitivity_threshold / 10
        self.peak_threshold = 100       # pascal

        self.previous_pressure = 0
        self.valley_pressure = 1e6

        # variables for enhancement controller
        self.base_speed = 0 # [0, 1]
        self.speed = 0      # [0, 1]
        self.min_speed = 0  # [0, 1]
        self.max_speed = 1  # [0, 1]
        self.ramp_time = 30 # s

    def update(self, pressure):
        dt = 1/50.0  # TODO: decouple from FOC-Stim sensor update rate
        self._update_arousal(dt, pressure)

        if self.arousal >= self.arousal_threshold:
            self._stop()

        self._update_speed(dt, self.arousal)

    def _update_arousal(self, dt, pressure):
        self.arousal *= np.exp(self.arousal_time_constant * dt)

        # effectively, this code sums all positive pressure increases,
        # but filters out increases that are small, like noise.
        # look into implementing this more elegantly.
        if pressure < self.previous_pressure:                           # pressure drops
            peak_size = self.previous_pressure - self.valley_pressure
            if peak_size > self.peak_threshold:
                self.arousal += peak_size
                self.valley_pressure = self.previous_pressure
            if pressure < self.valley_pressure:
                self.valley_pressure = pressure

        self.previous_pressure = pressure

    def _update_speed(self, dt, arousal):
        if self.ramp_time != 0:
            dy = (self.max_speed - self.min_speed) / float(self.ramp_time)
        else:
            dy = 0
        self.base_speed = self.base_speed + dy * dt
        self.base_speed = np.clip(self.base_speed, self.min_speed, self.max_speed)

        # reduce speed when arousal is high, but no lower than min speed.
        alter_perc = arousal / self.arousal_threshold
        self.speed = np.interp(alter_perc, [0, 1], [self.base_speed, self.min_speed])

        self.speed = np.clip(self.speed, self.min_speed, self.max_speed)

    def _stop(self):
        self.base_speed = self.min_speed
        self.speed = self.min_speed