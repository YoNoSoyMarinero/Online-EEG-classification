import numpy as np
import pandas as pd
from scipy.signal import welch
from scipy.stats import entropy
from scipy.signal import butter, filtfilt


def filter_data(c3, c4):
    fs = 160
    fcutlow = 8
    fcuthigh = 30
    nyq = 0.5 * fs
    Wn = [fcutlow/nyq, fcuthigh/nyq]
    b, a = butter(2, Wn, btype='band')
    return filtfilt(b, a, c3), filtfilt(b, a, c4)


class FeatureExtraction:

    @classmethod
    def featutre_extraction(self, c3, c4) :
        fs = 160
        c3, c4 = filter_data(c3, c4)
        features = []
        for ch in [c3, c4]:
            freqs, psd = welch(ch, fs=fs, nperseg=fs*2)
            spectral_entropy = entropy(psd)
            signal_variance = np.var(ch)
            peak_frequency = freqs[np.argmax(psd)]
            max_value = np.max(ch)
            features.append(spectral_entropy)
            features.append(signal_variance)
            features.append(peak_frequency)
            features.append(max_value)

        return features



