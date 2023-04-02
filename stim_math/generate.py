from stim_math import threephase


def generate_audio(alpha, beta, carrier_x, carrier_y,
                   point_calibration=None,
                   point_calibration_2=None,
                   modulation_1=None,
                   modulation_2=None,
                   hardware_calibration=None):
    # TODO: normalize norm(alpha, beta) <= 1

    L, R = threephase.ContinuousSineWaveform.generate(carrier_x, carrier_y, alpha, beta)
    # intensity = threephase.ContinuousSineWaveform.intensity(x, y)
    # L /= intensity
    # R /= intensity

    volume = 1
    if point_calibration is not None:
        volume *= point_calibration.get_scale(alpha, beta)
    if point_calibration_2 is not None:
        volume *= point_calibration_2.get_scale(alpha, beta)
    L *= volume
    R *= volume

    if modulation_1 is not None:
        L, R = modulation_1.modulate(L, R)
    if modulation_2 is not None:
        L, R = modulation_2.modulate(L, R)

    if hardware_calibration is not None:
        L, R = hardware_calibration.apply_transform(L, R)

    return L, R
