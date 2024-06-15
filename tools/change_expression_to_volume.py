from mido import MidiFile
from mido import MidiTrack
from mido import Message
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

def change(expression: int):
    new_volume = expression
    return new_volume

def expression_to_volume(midi: MidiFile):
    for track in midi.tracks:
        for msg in track:
            match msg.type:
                case "control_change":
                    if msg.is_cc(11):
                        msg.control=7

def clean_midi(midi_file: str):
    midi = MidiFile(midi_file)
    print("\n" + midi_file + "\n")
    expression_to_volume(midi)
    midi.save(midi_file.replace(".mid", "_e2v.mid"))


clean_midi(filedialog.askopenfilename())
input("Press the Enter key to continue: ") 