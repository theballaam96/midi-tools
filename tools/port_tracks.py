import mido
import tkinter as tk
from tkinter import filedialog
import small_libs.common as common

root = tk.Tk()
root.withdraw()


def copy_track(file_with_track, destination_file, output_file, track_num, channel_num):
    # Load the MIDI file
    source_mid = mido.MidiFile(file_with_track)
    dest_mid = mido.MidiFile(destination_file)

    # Create a new MIDI file to store the duplicated track
    duplicated_track = mido.MidiTrack()
    vacant_channels = list(range(16))

    for i, track in enumerate(dest_mid.tracks):
        for msg in track:
            if hasattr(msg, "channel") and msg.channel in vacant_channels:
                vacant_channels = [x for x in vacant_channels if x != msg.channel]
    for i, track in enumerate(source_mid.tracks):
        if i == track_num:
            for msg in track:
                duplicated_track.append(msg.copy())

    duplicated_channel = None
    if len(vacant_channels) == 0:
        raise Exception("No Vacant Channels")
    elif len(vacant_channels) > 1 and vacant_channels[0] == 9:
        # Try to avoid the percussion channel
        duplicated_channel = vacant_channels[1]
    else:
        duplicated_channel = vacant_channels[0]

    print(
        f"Placed duplication onto Track {len(dest_mid.tracks)}, Channel {duplicated_channel}"
    )
    for msg in duplicated_track:
        if hasattr(msg, "channel") and msg.channel == channel_num:
            msg.channel = duplicated_channel

    dest_mid.tracks.append(duplicated_track)

    # Save the new MIDI file
    dest_mid.save(output_file)


# Example usage
source_file = common.getMidiFile()
destination_file = filedialog.askopenfilename(title="Destination File")
output_file = destination_file.replace(".mid", "_portedtrack.mid")
track_num = 11  # Index of the track to port
channel_num = 9  # Channel number to port
copy_track(source_file, destination_file, output_file, track_num, channel_num)
