import pyxdf
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, detrend

# Replace 'your_file.xdf' with the path to your XDF file
xdf_file_path = '/Users/karthickchandrasekar/desktop/blockchainproject/iot/neha_default.xdf'

# Load the XDF file
streams, header = pyxdf.load_xdf(xdf_file_path)

# Print the available streams
print("Available streams:")
for i, stream in enumerate(streams):
    print(f"Stream {i+1}:")
    print(f"  Name: {stream['info']['name'][0]}")
    print(f"  Type: {stream['info']['type'][0]}")
    print(f"  Channel Count: {stream['info']['channel_count'][0]}")
    print(f"  Sampling Rate: {stream['info']['nominal_srate'][0]}")
    print("====================================")

# Assuming the first stream is the EEG data stream
eeg_stream = streams[0]
eeg_data = eeg_stream['time_series']
eeg_timestamps = eeg_stream['time_stamps']

# Convert timestamps to relative time in seconds
eeg_timestamps = eeg_timestamps - eeg_timestamps[0]

# Extract data for one channel (e.g., the first channel)
channel_data = eeg_data[:, 0]

# Validate the sampling rate from the stream metadata
sampling_rate = float(eeg_stream['info']['nominal_srate'][0])
print(f"Sampling rate from metadata: {sampling_rate} Hz")

# Data Cleaning Step 1: Remove NaN or Inf values
channel_data = np.nan_to_num(channel_data, nan=0.0, posinf=0.0, neginf=0.0)

# Data Cleaning Step 2: Detrend the data to remove linear trends
# channel_data = detrend(channel_data)

# Data Cleaning Step 3: Apply a band-pass filter to remove noise outside the desired frequency range (0.5-50 Hz)
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

sampling_rate = float(eeg_stream['info']['nominal_srate'][0])
lowcut = 0.5
highcut = 50.0
channel_data = bandpass_filter(channel_data, lowcut, highcut, sampling_rate)

# Apply FFT to the cleaned channel data
fft_result = np.fft.fft(channel_data)

# Calculate the frequency bins
n_samples = len(channel_data)
freq_bins = np.fft.fftfreq(n_samples, d=1/sampling_rate)

# Only use the positive frequencies (the result is symmetric)
positive_freq_indices = np.where(freq_bins >= 0)
freq_bins = freq_bins[positive_freq_indices]
fft_magnitude = np.abs(fft_result[positive_freq_indices])


# Function to isolate a specific frequency band
def isolate_frequency_band(fft_magnitude, freq_bins, low_freq, high_freq):
    band_indices = np.where((freq_bins >= low_freq) & (freq_bins <= high_freq))
    band_magnitude = np.zeros_like(fft_magnitude)
    band_magnitude[band_indices] = fft_magnitude[band_indices]
    return band_magnitude

# Isolate different wave types
delta = isolate_frequency_band(fft_magnitude, freq_bins, 0.5, 4)
theta = isolate_frequency_band(fft_magnitude, freq_bins, 4, 8)
alpha = isolate_frequency_band(fft_magnitude, freq_bins, 8, 13)
beta = isolate_frequency_band(fft_magnitude, freq_bins, 13, 30)
gamma = isolate_frequency_band(fft_magnitude, freq_bins, 30, 100)  # or 25 to 125 Hz

# Plot the isolated frequency bands with zoomed-in views
plt.figure(figsize=(12, 12))

plt.subplot(5, 1, 1)
plt.plot(freq_bins, delta)
plt.title('Delta Band (0.5-4 Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.xlim(0.5, 4)
plt.grid(True)

plt.subplot(5, 1, 2)
plt.plot(freq_bins, theta)
plt.title('Theta Band (4-8 Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.xlim(4, 8)
plt.grid(True)

plt.subplot(5, 1, 3)
plt.plot(freq_bins, alpha)
plt.title('Alpha Band (8-13 Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.xlim(8, 13)
plt.grid(True)

plt.subplot(5, 1, 4)
plt.plot(freq_bins, beta)
plt.title('Beta Band (13-30 Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.xlim(13, 30)
plt.grid(True)

plt.subplot(5, 1, 5)
plt.plot(freq_bins, gamma)
plt.title('Gamma Band (30-100 Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.xlim(30, 100)  # or 25 to 125 Hz if applicable
plt.grid(True)

plt.tight_layout()
plt.show()

# Print the first few values for debugging
print("First 10 samples of channel data:", channel_data[:10])
print("First 10 FFT results (magnitude):", fft_magnitude[:10])
print("Frequency bins (positive):", freq_bins[:10])