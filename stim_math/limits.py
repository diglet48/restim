class Carrier:
    min = 300
    max = 1500


class ModulationFrequency:
    min = 0
    max = 100


class ModulationBias:
    min = -.999
    max = .999

# the minimum 'on' or 'off' time for amplitude modulation
minimum_amplitude_modulation_feature_length = 3