"""
Version 1.0.1

- This script duplicates a desired track in a MIDI.
"""

from mido import MidiFile, MidiTrack

from small_libs.common import getMidiFile


def duplicate_track_channel(midi, track_num, channel_num) -> MidiFile:

    # Create a new MIDI file to store the duplicated track
    duplicated_track = MidiTrack()
    vacant_channels = list(range(16))

    for i, track in enumerate(midi.tracks):
        for msg in track:
            if hasattr(msg, "channel") and msg.channel in vacant_channels:
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

    print(
        f"Placed duplication onto Track {len(midi.tracks)}, Channel {duplicated_channel}"
    )
    for msg in duplicated_track:
        if hasattr(msg, "channel") and msg.channel == channel_num:
            msg.channel = duplicated_channel

    midi.tracks.append(duplicated_track)

    return midi


def main() -> None:
    input_file, path = getMidiFile(path=True)
    track_num = int(input("Index of the track to duplicate: "))
    channel_num = int(input("Channel number to duplicate: "))
    output_file = duplicate_track_channel(input_file, track_num, channel_num)
    output_file.save(path.replace(".mid", "_duplicatedtrack.mid"))


if __name__ == "__main__":
    main()