from stim_math import threephase
from stim_math.audio_gen.base_classes import AudioModifyAlgorithm
from stim_math.threephase_parameter_manager import ThreephaseParameterManager


class ThreePhaseModifyAlgorithm(AudioModifyAlgorithm):
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__()
        self.params = params

    def preferred_channel_count(self):
        return [2]

    def channel_mapping(self, channel_count):
        return [0, 1]

    def modify_audio(self, in_data):
        L, R = in_data.T
        hw = threephase.ThreePhaseHardwareCalibration(self.params.calibration_neutral.last_value(),
                                                      self.params.calibration_right.last_value())
        L, R = hw.apply_transform(L, R)
        return L, R
