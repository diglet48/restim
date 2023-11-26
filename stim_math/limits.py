class Mk312CarrierFrequency:
    min = 10
    max = 2000


class ModulationFrequency:
    min = 0
    max = 100


class ModulationBias:
    min = -.999
    max = .999


class PulseCarrierFrequency:
    min = 300
    max = 5000


class PulseFrequency:
    min = 1
    max = 300


class PulseWidth:
    min = 3
    max = 100

# the minimum 'on' or 'off' time for amplitude modulation
minimum_amplitude_modulation_feature_length = 3