from mido import MidiFile, MetaMessage
import tkinter as tk
from tkinter import filedialog
import small_libs.common as common

root = tk.Tk()
root.withdraw()


def insert_tempo(midi: MidiFile):
    midi.tracks[0].insert(0, MetaMessage("set_tempo"))


def clean_midi(midi_file: str):
    midi = MidiFile(midi_file)
    print("\n" + midi_file + "\n")
    insert_tempo(midi)
    midi.save(midi_file.replace(".mid", "_tinserted.mid"))


clean_midi(common.getMidiFile())
input("Press the Enter key to continue: ")
