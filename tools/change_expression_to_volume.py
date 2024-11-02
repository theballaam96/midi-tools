from mido import MidiFile
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
global currentVolume

def expression_to_volume(midi: MidiFile):
    for track in midi.tracks:
        for msg in track:
            match msg.type:
                case "control_change":
                    if msg.is_cc(7):
                        currentVolume = msg.value
                    elif msg.is_cc(11):
                        newVolume = (msg.value / 127)*currentVolume
                        msg.value = int(newVolume)
                        msg.control = 7

def clean_midi(midi_file: str):
    midi = MidiFile(midi_file)
    print("\n" + midi_file + "\n")
    expression_to_volume(midi)
    midi.save(midi_file.replace(".mid", "_e2v.mid"))


clean_midi(filedialog.askopenfilename())
input("Press the Enter key to continue: ") 