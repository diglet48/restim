

class SensorNodeInterface:
    TITLE = ""
    DESCRIPTION = ""

    def __init__(self):
        super().__init__()
        self._node_enabled = False

    # implement these functions in your subclass:
    # def new_as5311_sensor_data(self, data: AS5311Data):
    # def new_imu_sensor_data(self, data: IMUData):
    # def new_pressure_sensor_data(self, data: PressureData):

    def enable_node(self):
        self._node_enabled = True

    def disable_node(self):
        self._node_enabled = False

    def is_node_enabled(self):
        return self._node_enabled

    def process(self, parameters):
        """
        :param parameters: a dict such as {'volume': 0.5, 'alpha': -0.4}
        :return:

        Modify the parameter dict in-place.

        For safety reasons, it is strongly recommended only to decrease the volume,
        and never increase it in this function.
        """
        pass

