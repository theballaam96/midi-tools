import mido
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

def duplicate_track_channel(input_file, output_file, track_num, channel_num):
    # Load the MIDI file
    mid = mido.MidiFile(input_file)

    # Create a new MIDI file to store the duplicated track
    duplicated_track = mido.MidiTrack()
    vacant_channels = list(range(16))

    for i, track in enumerate(mid.tracks):
        for msg in track:
            if hasattr(msg, 'channel') and msg.channel in vacant_channels:
                vacant_channels = [x for x in vacant_channels if x != msg.channel]
            if i == track_num:
                duplicated_track.append(msg.copy())

    duplicated_channel = None
    if len(vacant_channels) == 0:
        raise Exception("No Vacant Channels")
    elif len(vacant_channels) > 1 and vacant_channels[0] == 9:
        # Try to avoid the percussion channel
        duplicated_channel = vacant_channels[1]
    else:
        duplicated_channel = vacant_channels[0]

    print(f"Placed duplication onto Track {len(mid.tracks)}, Channel {duplicated_channel}")
    for msg in duplicated_track:
        if hasattr(msg, 'channel') and msg.channel == channel_num:
            msg.channel = duplicated_channel

    mid.tracks.append(duplicated_track)

    # Save the new MIDI file
    mid.save(output_file)

# Example usage
input_file = filedialog.askopenfilename()
output_file = input_file.replace(".mid", "_duplicatedtrack.mid")
track_num = 8  # Index of the track to duplicate
channel_num = 6  # Channel number to duplicate
duplicate_track_channel(input_file, output_file, track_num, channel_num)