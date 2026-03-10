from mido import MidiFile, MidiTrack
from small_libs.common import getMidiFile


def copy_track(source_mid: MidiFile, dest_mid: MidiFile, track_num: int, channel_num: int) -> MidiFile:
    # Create a new MIDI file to store the duplicated track
    duplicated_track = MidiTrack()
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
    return dest_mid


def main() -> None:
    # Example usage
    source_file = getMidiFile(title="Source File")
    destination_file, destination_path = getMidiFile(path=True, title="Destination File")
    track_num = 11  # Index of the track to port
    channel_num = 9  # Channel number to port
    ported_midi = copy_track(source_file, destination_file, track_num, channel_num)
    ported_midi.save(destination_path.replace(".mid", "_portedtrack.mid"))


if __name__ == "__main__":
    main()