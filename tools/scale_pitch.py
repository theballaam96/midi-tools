from mido import MidiFile
from mido import MidiTrack
from mido import Message
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

def multiply_pitch(pitch: int):
    new_pitch = pitch+4096
    clamped_pitch = max(min(8191, new_pitch), -8192)
    return clamped_pitch

def fix_pitch_and_volumes(midi: MidiFile, todo: str):
    for track in midi.tracks:
        for msg in track:
            match todo:
                case "pitch":
                    match msg.type:
                        case "pitchwheel":
                            msg.pitch = multiply_pitch(msg.pitch)

def clean_midi(midi_file: str):
    midi = MidiFile(midi_file)
    print("\n" + midi_file + "\n")
    fix_pitch_and_volumes(midi, "pitch")  # pitch, volume, or both
    midi.save(midi_file.replace(".mid", "_scaled.mid"))


clean_midi(filedialog.askopenfilename())
input("Press the Enter key to continue: ") 
