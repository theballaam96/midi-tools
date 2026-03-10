from mido import MidiFile
from small_libs.common import getMidiFile


def convert_type0_type1(type_0: MidiFile) -> MidiFile:
    if type_0.type != 0:
        raise TypeError("MIDI must be type 0")
    type_1 = MidiFile(
        type=1,
        ticks_per_beat=type_0.ticks_per_beat)
    time = 0
    channels = {}
    for item in type_0.tracks[0]:
        msg = item.copy()

        if hasattr(msg, 'time'):
            time += msg.time

        channel = msg.channel if hasattr(msg, 'channel') else -1
        if channel not in channels:
            channels[channel] = {
                'time': 0,
                'msg': []
            }
        chl = channels[channel]

        if hasattr(msg, 'time'):
            msg.time = time - chl['time']
            chl['time'] = time
        chl['msg'].append(msg)

    for chan in channels:
        track = type_1.add_track()
        track.extend(channels[chan]['msg'])

    return type_1


def main() -> None:
    OLD_MIDI, path = getMidiFile()
    NEW_MIDI = convert_type0_type1(OLD_MIDI)
    NEW_MIDI.save(path.replace(".mid", "_converted.mid"))


if __name__ == "__main__":
    main()