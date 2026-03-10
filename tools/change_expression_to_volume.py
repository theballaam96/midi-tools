from mido import MidiFile
from small_libs.common import getMidiFile

global currentVolume


def expression_to_volume(midi: MidiFile) -> None:
    for track in midi.tracks:
        for msg in track:
            match msg.type:
                case "control_change":
                    if msg.is_cc(7):
                        currentVolume = msg.value
                    elif msg.is_cc(11):
                        newVolume = (msg.value / 127) * currentVolume
                        msg.value = int(newVolume)
                        msg.control = 7


def main() -> None:
    midi, path = getMidiFile()
    expression_to_volume(midi)
    midi.save(path.replace(".mid", "_e2v.mid"))


if __name__ == "__main__":
    main()
