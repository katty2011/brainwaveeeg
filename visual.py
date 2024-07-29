import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def visualize_eeg(csv_filename):
    # Load the CSV file
    data = pd.read_csv(csv_filename)

    # Create a new figure with a specific size
    plt.figure(figsize=(12, 8))

    # Plot each EEG channel
    channels = ['TP9', 'AF7', 'AF8', 'TP10']
    colors = ['r', 'g', 'b', 'm']  # Red, Green, Blue, Magenta

    # Use the index as the time axis
    time_axis = data.index / 256  # Assuming 256 Hz sampling rate, convert to seconds

    for channel, color in zip(channels, colors):
        plt.plot(time_axis, data[channel], color=color, label=channel, linewidth=0.5)

    # Customize the plot
    plt.title('EEG Data from Muse 2')
    plt.xlabel('Time (seconds)')
    plt.ylabel('EEG Signal (μV)')
    plt.legend()
    plt.grid(True)

    # Add a zoomed inset for a detailed view of a 5-second window
    axins = inset_axes(plt.gca(), width="40%", height="30%", loc=1)
    for channel, color in zip(channels, colors):
        axins.plot(time_axis, data[channel], color=color, linewidth=0.5)
    axins.set_xlim(0, 5)  # Show first 5 seconds in detail
    axins.set_title("First 5 seconds (detailed view)")
    axins.grid(True)

    # Show the plot
    plt.tight_layout()
    plt.show()

# Replace 'your_eeg_data.csv' with the actual filename of your CSV
csv_filename = '/Users/karthickchandrasekar/Desktop/BlockChainProject/iot/EEG_recording_2024-07-29-02.17.10.csv'
visualize_eeg(csv_filename)