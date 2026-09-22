class ModulationFrequency:
    min = 0
    max = 100


class ModulationBias:
    min = -.999
    max = .999


class PulseFrequency:   # in cycles, also for FOC
    min = 1
    max = 200   # actually limited by InterPulseIntervalDuration.min


class PulseWidth:   # in cycles
    min = 3
    max = 20


class PulseRiseTime:    # in cycles
    min = 2
    max = 100


class PulseDuration:    # in seconds, also for FOC
    min = 0
    max = 0.035         # FOC limitation


class InterPulseIntervalDuration:   # in seconds, also for FOC
    min = 0.005
    max = 1


# the minimum 'on' or 'off' time for amplitude modulation
minimum_amplitude_modulation_feature_length = 3


class CarrierFrequencyFOC:
    min = 300   # Hz
    max = 2000

class WaveformAmpltiudeFOC:
    min = 0.01  # Amperes
    max = 0.20

