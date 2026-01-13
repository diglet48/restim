import numpy as np


# scipy implementation
# class HighPass:
#     def __init__(self, bandlimit, samplerate):
#         self.sos = scipy.signal.butter(1, bandlimit, 'highpass', fs=samplerate, output='sos')
#         self.zi = scipy.signal.sosfilt_zi(self.sos)
#         self.zi *= 0
#
#     def update(self, data):
#         out, self.zi = scipy.signal.sosfilt(self.sos, [data], zi=self.zi)
#         return out[0]

# numpy implementation, does not depend on scipy
# implements 1st order butterworth filter
class HighPass:
    def __init__(self, bandlimit, samplerate):
        K = np.tan(np.pi * bandlimit / samplerate)
        alpha = (1 - K) / (1 + K)
        self.b = np.array([(1 + alpha) / 2, -(1 + alpha) / 2])
        self.a = np.array([1, -alpha])

        self.zi = np.array([0])

    def update(self, data):
        out = self.b[0] * data + self.zi
        self.zi = self.b[1] * data - self.a[1] * out
        return out[0]