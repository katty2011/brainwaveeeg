import pyxdf
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, detrend
from scipy.stats import ttest_ind


# Define band-pass filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a


def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y


# Load and preprocess data for both participants
def load_and_preprocess(xdf_file_path):
    streams, header = pyxdf.load_xdf(xdf_file_path)
    eeg_stream = streams[0]
    eeg_data = eeg_stream['time_series']
    sampling_rate = float(eeg_stream['info']['nominal_srate'][0])

    cleaned_data = []
    for channel in range(eeg_data.shape[1]):
        channel_data = eeg_data[:, channel]
        channel_data = np.nan_to_num(channel_data, nan=0.0, posinf=0.0, neginf=0.0)
        channel_data = detrend(channel_data)
        channel_data = bandpass_filter(channel_data, 0.5, 50.0, sampling_rate)
        cleaned_data.append(channel_data)
    return np.array(cleaned_data), sampling_rate


# Compute power spectrum for each channel
def compute_power_spectrum(data, sampling_rate):
    n_samples = data.shape[1]
    fft_result = np.fft.fft(data, axis=1)
    freq_bins = np.fft.fftfreq(n_samples, d=1 / sampling_rate)
    positive_freq_indices = np.where(freq_bins >= 0)
    freq_bins = freq_bins[positive_freq_indices]
    power_spectrum = np.abs(fft_result[:, positive_freq_indices[0]]) ** 2
    return power_spectrum, freq_bins


# Ensure the pre and post data have the same number of samples
def trim_to_min_samples(pre_data, post_data):
    min_samples = min(pre_data.shape[1], post_data.shape[1])
    pre_data_trimmed = pre_data[:, :min_samples]
    post_data_trimmed = post_data[:, :min_samples]
    return pre_data_trimmed, post_data_trimmed


# Load pre and post music listening data for both participants
pre_xdf_file_path = '/Users/karthickchandrasekar/Desktop/BlockChainProject/iot/maggie_1.xdf'
post_xdf_file_path = 'post_music.xdf'

pre_data, sampling_rate = load_and_preprocess(pre_xdf_file_path)
post_data, _ = load_and_preprocess(post_xdf_file_path)

# Trim data to have the same number of samples
pre_data, post_data = trim_to_min_samples(pre_data, post_data)

# Compute power spectra
pre_power_spectrum, freq_bins = compute_power_spectrum(pre_data, sampling_rate)
post_power_spectrum, _ = compute_power_spectrum(post_data, sampling_rate)

# Average power spectra across channels
pre_power_avg = np.mean(pre_power_spectrum, axis=0).flatten()  # Flatten the array to ensure correct shape
post_power_avg = np.mean(post_power_spectrum, axis=0).flatten()  # Flatten the array to ensure correct shape

# Plot power spectra
plt.figure(figsize=(12, 6))
plt.plot(freq_bins, pre_power_avg, label='Pre Music')
plt.plot(freq_bins, post_power_avg, label='Post Music')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power')
plt.title('Average Power Spectrum Before and After Listening to Calming Music')
plt.legend()
plt.grid(True)
plt.show()

# Statistical comparison
stat, p = ttest_ind(pre_power_spectrum, post_power_spectrum, axis=0)

# Ensure p is 1-dimensional for indexing
p = p.flatten()

# Find significant frequencies
significant_freqs = freq_bins[p < 0.05]

print(f"Significant frequency differences: {significant_freqs}")
print(f"p-values: {p[p < 0.05]}")
