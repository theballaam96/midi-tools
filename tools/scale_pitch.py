"""
Version 1.0.1

- This script multiplies all of the pitchwheel events in a MIDI file by a desired factor.
"""

from mido import MidiFile

from small_libs.common import getMidiFile


def multiply_pitch(midi: MidiFile, factor: float) -> None:
    for track in midi.tracks:
        for msg in track:
            if msg.type == "pitchwheel":
                new_pitch = round(msg.pitch * factor)
                clamped_pitch = max(min(8191, new_pitch), -8192)
                msg.pitch = clamped_pitch


def main() -> None:
    midi, path = getMidiFile(path=True)
    factor = float(input("Scale factor: "))
    multiply_pitch(midi, factor)
    midi.save(path.replace(".mid", "_scaled.mid"))


if __name__ == "__main__":
    main()