import asyncio
import pandas as pd
import numpy as np
from scipy import signal
from pylsl import StreamInlet, resolve_stream
import time

# Constants
RECORD_DURATION = 60  # Duration in seconds
MUSE_ADDRESS = "170A1E6D-C386-2E20-6012-76E4C5586FD7"  # Replace with your Muse device's MAC address


async def connect_to_muse(address):
    """
    Attempt to connect to the Muse device using muselsl.

    Args:
    address (str): MAC address of the Muse device

    Returns:
    subprocess.Process: The process running the muselsl stream
    """
    print(f"Attempting to connect to Muse device at {address}")
    process = await asyncio.create_subprocess_shell(
        f"muselsl stream --address {address}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return process


async def record_eeg(duration):
    """
    Record EEG data from the connected Muse device.

    Args:
    duration (int): Duration of recording in seconds

    Returns:
    list: List of EEG data samples, each sample is a list of channel values and a timestamp
    """
    print("Looking for an EEG stream...")
    streams = resolve_stream('type', 'EEG')

    if not streams:
        print("No EEG stream found. Make sure your Muse device is connected.")
        return None

    inlet = StreamInlet(streams[0])

    print(f"Recording EEG data for {duration} seconds...")
    start_time = time.time()
    eeg_data = []

    while time.time() - start_time < duration:
        sample, timestamp = inlet.pull_sample()
        eeg_data.append(sample + [timestamp])  # Add timestamp to the sample

    print("Recording completed.")
    return eeg_data


def save_to_csv(eeg_data, filename):
    """
    Save the recorded EEG data to a CSV file.

    Args:
    eeg_data (list): List of EEG data samples
    filename (str): Name of the file to save the data

    Returns:
    str: Name of the saved file, or None if saving failed
    """
    if not eeg_data:
        print("No EEG data to save.")
        return None

    columns = ['TP9', 'AF7', 'AF8', 'TP10', 'AUX', 'Timestamp']
    df = pd.DataFrame(eeg_data, columns=columns)
    df.to_csv(filename, index=False)
    print(f"EEG data saved to {filename}")
    return filename


async def record_and_save(filename):
    """
    Connect to Muse, record EEG data, and save it to a file.

    Args:
    filename (str): Name of the file to save the recorded data

    Returns:
    str: Name of the saved file, or None if recording or saving failed
    """
    muse_process = await connect_to_muse(MUSE_ADDRESS)
    print("Waiting for EEG stream to start...")
    await asyncio.sleep(5)  # Give some time for the stream to start
    eeg_data = await record_eeg(RECORD_DURATION)
    muse_process.terminate()
    await muse_process.wait()
    if eeg_data:
        return save_to_csv(eeg_data, filename)
    else:
        print("Failed to record EEG data.")
        return None


def calculate_band_powers(eeg_data):
    """
    Calculate the power in different frequency bands for a single EEG channel.

    Args:
    eeg_data (pd.Series): EEG data for a single channel

    Returns:
    dict: Power in each frequency band
    """
    sampling_rate = 256  # Muse headband sampling rate

    # Define frequency bands
    bands = {
        'Delta': (0.5, 4),
        'Theta': (4, 8),
        'Alpha': (8, 13),
        'Beta': (13, 30),
        'Gamma': (30, 100)
    }

    # Calculate power spectral density
    f, psd = signal.welch(eeg_data, fs=sampling_rate, nperseg=256)

    # Calculate average power in each band
    band_powers = {}
    for band, (low, high) in bands.items():
        band_powers[band] = np.mean(psd[(f >= low) & (f <= high)])

    return band_powers


def calculate_focus_score(changes):
    """
    Calculate a simplified focus score based on changes in EEG band powers.

    Focus Score Computation Logic:
    1. We assign weights to each frequency band:
       - Negative weights to Delta (-0.1), Theta (-0.1), and Alpha (-0.2)
       - Positive weights to Beta (0.3) and Gamma (0.3)
    2. These weights reflect that:
       a) Decreases in lower frequency bands (Delta, Theta, Alpha) often indicate increased alertness
       b) Increases in higher frequency bands (Beta, Gamma) suggest increased cognitive activity
    3. The score is computed as a weighted sum of the percentage changes in each band
    4. A positive score suggests increased focus/cognitive engagement, while a negative score suggests decreased focus

    Args:
    changes (dict): Percentage changes in each frequency band

    Returns:
    float: Calculated focus score
    """
    focus_score = (
            -0.1 * changes['Delta']  # Decrease in Delta contributes positively to focus
            - 0.1 * changes['Theta']  # Decrease in Theta contributes positively to focus
            - 0.2 * changes['Alpha']  # Decrease in Alpha often indicates increased alertness
            + 0.3 * changes['Beta']  # Increase in Beta suggests increased cognitive activity
            + 0.3 * changes['Gamma']  # Increase in Gamma suggests increased cognitive processing
    )
    return focus_score


def interpret_focus_score(score):
    """
    Interpret the calculated focus score.

    Args:
    score (float): The calculated focus score

    Returns:
    str: Interpretation of the focus score
    """
    if score > 10:
        return "Significant increase in focus and cognitive engagement"
    elif score > 0:
        return "Moderate increase in focus and cognitive engagement"
    elif score > -10:
        return "Slight decrease in focus and cognitive engagement"
    else:
        return "Significant decrease in focus and cognitive engagement"


def compare_eeg_data(pre_music_file, post_music_file):
    """
    Compare pre-music and post-music EEG data to calculate changes in different frequency bands.

    Args:
    pre_music_file (str): Filename of pre-music EEG data
    post_music_file (str): Filename of post-music EEG data

    Returns:
    tuple: (changes in each frequency band, focus score, interpretation of focus score)
    """
    # Load EEG data from CSV files
    pre_music_data = pd.read_csv(pre_music_file)
    post_music_data = pd.read_csv(post_music_file)

    channels = ['AF7', 'AF8']  # Focus on frontal channels
    pre_music_powers = []
    post_music_powers = []

    # Calculate band powers for each channel in both pre and post music data
    for channel in channels:
        pre_powers = calculate_band_powers(pre_music_data[channel])
        post_powers = calculate_band_powers(post_music_data[channel])

        pre_music_powers.append(pre_powers)
        post_music_powers.append(post_powers)

        print(f"Channel {channel}:")
        for band in pre_powers.keys():
            print(f"  {band} - Pre: {pre_powers[band]:.4f}, Post: {post_powers[band]:.4f}")

    # Calculate average powers across channels
    avg_pre_powers = {band: np.mean([powers[band] for powers in pre_music_powers]) for band in
                      pre_music_powers[0].keys()}
    avg_post_powers = {band: np.mean([powers[band] for powers in post_music_powers]) for band in
                       post_music_powers[0].keys()}

    # Calculate percentage changes
    changes = {band: ((avg_post_powers[band] - avg_pre_powers[band]) / avg_pre_powers[band]) * 100 for band in
               avg_pre_powers.keys()}

    # Calculate focus score and get interpretation
    focus_score = calculate_focus_score(changes)
    interpretation = interpret_focus_score(focus_score)

    return changes, focus_score, interpretation


async def main():
    """
    Main function to run the EEG recording and analysis process.
    """
    print("Recording pre-music EEG data...")
    pre_music_file = await record_and_save(".venv/pre_music_eeg.csv")

    if not pre_music_file:
        print("Failed to record pre-music EEG data. Exiting.")
        return

    input("Press Enter when you're ready to record post-music EEG data...")

    print("Recording post-music EEG data...")
    post_music_file = await record_and_save(".venv/post_music_eeg.csv")

    if not post_music_file:
        print("Failed to record post-music EEG data. Exiting.")
        return

    changes, focus_score, interpretation = compare_eeg_data(pre_music_file, post_music_file)

    print("\nChanges in EEG frequency bands:")
    for band, change in changes.items():
        print(f"{band}: {change:.2f}%")

    print(f"\nFocus Score: {focus_score:.2f}")
    print(f"Interpretation: {interpretation}")


if __name__ == "__main__":
    asyncio.run(main())
