import asyncio
import subprocess
import pandas as pd
import numpy as np
from pylsl import StreamInlet, resolve_stream
import time

RECORD_DURATION = 60  # Duration in seconds


async def stream_eeg(address):
    print(f"Attempting to connect to Muse device at {address}")
    process = await asyncio.create_subprocess_shell(
        f"muselsl stream --address {address}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    return process


async def record_eeg(duration):
    print("Looking for an EEG stream...")
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])

    print(f"Recording EEG data for {duration} seconds...")
    start_time = time.time()
    eeg_data = []

    while time.time() - start_time < duration:
        sample, timestamp = inlet.pull_sample()
        eeg_data.append(sample + [timestamp])  # Add timestamp to the sample

    print("Recording completed.")
    return eeg_data


def save_to_csv(eeg_data, filename="eeg_recording.csv"):
    columns = ['TP9', 'AF7', 'AF8', 'TP10', 'AUX', 'Timestamp']
    df = pd.DataFrame(eeg_data, columns=columns)
    df.to_csv(filename, index=False)
    print(f"EEG data saved to {filename}")
    return filename


async def main():
    # Replace this with your Muse device's MAC address
    muse_address = "170A1E6D-C386-2E20-6012-76E4C5586FD7"  # Replace XX:XX with the last two pairs from your device's MAC address

    stream_process = await stream_eeg(muse_address)

    print("Waiting for EEG stream to start...")
    await asyncio.sleep(5)  # Give some time for the stream to start

    eeg_data = await record_eeg(RECORD_DURATION)

    print("Stopping the EEG stream...")
    stream_process.terminate()
    await stream_process.wait()

    if eeg_data:
        csv_file = save_to_csv(eeg_data)
        return csv_file
    else:
        print("Failed to record EEG data.")
        return None


if __name__ == "__main__":
    csv_file = asyncio.run(main())
    if csv_file:
        print(f"EEG data has been recorded and saved to {csv_file}")
        print("You can now use this CSV file for further analysis or visualization.")