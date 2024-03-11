# Checks a MIDI file to see if there are any overlapping notes
# An overlapping note is defined as two MIDI on events in sequence
import math
from mido import MidiFile, tick2second
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

input_midi = MidiFile(filedialog.askopenfilename())

notes = {} # stores which note is being held when iterating through each event
tempo = 120 # default, tempo will be read from the file
numerator = 4 # default, will be read from the file
absolute_ticks = 0 # contains the current time when processing each event

def note_to_name(note):
    abs_note = note
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = math.floor((note / 12) - 1)
    note_index = (note % 12)
    note = notes[note_index]
    return f'{note}{octave} ({abs_note})'

# process MIDI messages
for original_track in input_midi.tracks:
    absolute_ticks = 0
    for msg in original_track:
        if msg.type == 'time_signature':
            numerator = msg.numerator
        if msg.type != 'end_of_track':
            absolute_ticks += msg.time
        if msg.type == 'set_tempo':
            tempo = msg.tempo
        if msg.type == 'note_off' or msg.type == 'note_on' and msg.velocity == 0:
            try:
                del notes[msg.note]
            except:
                pass
        if msg.type == 'note_on':
            if msg.note in notes:
                print(f'Overlapping note {note_to_name(msg.note)} at bar {absolute_ticks / input_midi.ticks_per_beat / numerator + 1} (Tick {absolute_ticks}, Channel {msg.channel})')
            notes[msg.note] = msg