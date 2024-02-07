from stim_math import threephase
from stim_math.audio_gen.base_classes import AudioModifyAlgorithm
from stim_math.audio_gen.params import ThreephaseCalibrationParams


class ThreePhaseModifyAlgorithm(AudioModifyAlgorithm):
    def __init__(self, calibrate: ThreephaseCalibrationParams):
        super().__init__()
        self.calibrate = calibrate

    def channel_count(self) -> int:
        return 2

    def modify_audio(self, in_data):
        L, R = in_data.T
        hw = threephase.ThreePhaseHardwareCalibration(self.calibrate.neutral.last_value(),
                                                      self.calibrate.right.last_value())
        L, R = hw.apply_transform(L, R)
        return L, R
