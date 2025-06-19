class ModulationFrequency:
    min = 0
    max = 100


class ModulationBias:
    min = -.999
    max = .999


class PulseFrequency:
    min = 1
    max = 300


class PulseWidth:
    min = 3
    max = 100


class PulseRiseTime:
    min = 2
    max = 100


# the minimum 'on' or 'off' time for amplitude modulation
minimum_amplitude_modulation_feature_length = 3


class CarrierFrequencyFOC:
    min = 500   # Hz
    max = 2000

class WaveformAmpltiudeFOC:
    min = 0.01  # Amperes
    max = 0.15