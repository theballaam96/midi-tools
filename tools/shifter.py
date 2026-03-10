from mido import MidiFile
from small_libs.common import getMidiFile


def shiftMidi(midi: MidiFile, path: str, shift: int) -> MidiFile:
    for track in midi.tracks:
        performed_shift = False
        for msg in track:
            if hasattr(msg, "time"):
                if msg.type == "note_on":
                    if not performed_shift:
                        msg.time += shift
                    performed_shift = True
    return midi


def main() -> None:
    midi, path = getMidiFile()
    shifty = int(input("Shift amount: "))
    shifted_midi = shiftMidi(midi, path, shifty)
    shifted_midi.save(path.replace(".mid", "_shifted.mid"))


if __name__ == "__main__":
    main()