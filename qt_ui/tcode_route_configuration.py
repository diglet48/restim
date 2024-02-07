from PyQt5.QtCore import QSettings

default_values = {
    'alpha' : ['L0', True, -1, 1],
    'beta' : ['L1', True, -1, 1],
    'volume' : ['L2', False, 0, 1],
    'carrier' : ['L3', False, 500, 1000],
    'vibration-1-frequency' : ['L4', False, 0, 100],
}


class ThreephaseRouteConfigurationAxis:
    def __init__(self, key):
        self.key = key
        self.enabled = False
        self.axis = 'L0'
        self.left = 0
        self.right = 1

        self.reload()

    def construct_key(self, prop):
        return f'threephase/{self.key}-{prop}'

    def reload(self):
        settings = QSettings()
        defaults = default_values[self.key]
        self.enabled = settings.value(self.construct_key('enabled'), defaults[1], bool)
        self.axis = settings.value(self.construct_key('axis'), defaults[0], str)
        self.left = settings.value(self.construct_key('left'), defaults[2], float)
        self.right = settings.value(self.construct_key('right'), defaults[3], float)

    def save(self):
        settings = QSettings()
        settings.setValue(self.construct_key('enabled'), self.enabled)
        settings.setValue(self.construct_key('axis'), self.axis)
        settings.setValue(self.construct_key('left'), self.left)
        settings.setValue(self.construct_key('right'), self.right)


class ThreephaseRouteConfiguration:
    def __init__(self):
        self.alpha = ThreephaseRouteConfigurationAxis('alpha')
        self.beta = ThreephaseRouteConfigurationAxis('beta')
        self.carrier = ThreephaseRouteConfigurationAxis('carrier')
        self.volume = ThreephaseRouteConfigurationAxis('volume')
        self.vibration_1_frequency = ThreephaseRouteConfigurationAxis('vibration-1-frequency')

    def save(self):
        self.alpha.save()
        self.beta.save()
        self.carrier.save()
        self.volume.save()
        self.vibration_1_frequency.save()