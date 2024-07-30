# EEG Analysis with Muse Headband

This project allows you to record and analyze EEG data using a Muse headband to measure changes in brain activity before and after listening to music. It calculates power in different frequency bands and provides a focus score based on the changes observed.

## Prerequisites

- Muse headband
- Python 3.7+
- `muselsl` command-line tool

## Dependencies

This project relies on several Python libraries. Here's a list of the required libraries and their purposes:

1. **asyncio**
   - Purpose: Provides support for asynchronous programming, allowing the script to handle I/O-bound operations efficiently.
   - Usage: Used for asynchronous execution of Muse connection and data recording.

2. **pandas**
   - Purpose: Data manipulation and analysis library.
   - Usage: Used for creating and manipulating DataFrames to store and process EEG data.

3. **numpy**
   - Purpose: Numerical computing library for Python.
   - Usage: Provides support for large, multi-dimensional arrays and matrices, along with mathematical functions to operate on these arrays.

4. **scipy**
   - Purpose: Library for scientific computing.
   - Usage: Specifically, the `signal` module is used for calculating power spectral density of EEG data.

5. **pylsl**
   - Purpose: Python interface to the Lab Streaming Layer (LSL), a system for synchronizing streaming data.
   - Usage: Used to receive real-time EEG data streams from the Muse headband.

6. **muselsl**
   - Purpose: Command-line tool for streaming data from Muse devices.
   - Usage: Used to establish a connection with the Muse headband and start the EEG data stream.

## Setup

1. **Install dependencies:**

   ```
   pip install asyncio pandas numpy scipy pylsl muselsl
   ```

2. **Encode Muse MAC Address:**

   Replace the `MUSE_ADDRESS` constant in the script with your Muse device's MAC address:

   ```python
   MUSE_ADDRESS = "YOUR_MUSE_MAC_ADDRESS"
   ```

   To find your Muse's MAC address:
   - On macOS: Open Terminal and run `system_profiler SPBluetoothDataType`
   - On Windows: Open Command Prompt and run `bluetoothview`
   - On Linux: Open Terminal and run `bluetoothctl`, then `scan on`

## Usage

1. **Prepare the Muse headband:**
   - Turn on your Muse headband
   - Ensure it's properly fitted on your head

2. **Run the script:**

   ```
   python eeg_analysis.py
   ```

3. **Follow the prompts:**
   - The script will first record pre-music EEG data for 60 seconds
   - After the first recording, you'll be prompted to start listening to music
   - Press Enter when you're ready to record post-music EEG data
   - The script will record another 60 seconds of EEG data

4. **Review the results:**
   - The script will display changes in EEG frequency bands
   - A focus score and interpretation will be provided

## Expected Output

The script will generate two CSV files:
- `pre_music_eeg.csv`: Contains the pre-music EEG data
- `post_music_eeg.csv`: Contains the post-music EEG data

The console output will show:
- Changes in each frequency band (Delta, Theta, Alpha, Beta, Gamma)
- A calculated focus score
- An interpretation of the focus score

Example output:
```
Changes in EEG frequency bands:
Delta: -5.23%
Theta: -2.15%
Alpha: -8.76%
Beta: 12.34%
Gamma: 7.89%

Focus Score: 6.78
Interpretation: Moderate increase in focus and cognitive engagement
```

## Troubleshooting

- If you encounter connection issues, ensure your Muse headband is charged and properly paired with your computer
- Verify that the MAC address in the script matches your Muse device
- Check that all dependencies are correctly installed

## Contributing

Feel free to fork this project and submit pull requests with improvements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
