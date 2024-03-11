import mido
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

def shiftMidi(midi_file: str, shift: int):
    mid = mido.MidiFile(midi_file)
    for track in mid.tracks:
        performed_shift = False
        for msg in track:
            if hasattr(msg, 'time'):
                if msg.type == "note_on":
                    if not performed_shift:
                        msg.time += shift
                    performed_shift = True
    mid.save(midi_file.replace(".mid", "_shifted.mid"))

shiftMidi(filedialog.askopenfilename(), -120)