"""
Common functions to reuse in most files, just to make starting seperate files more consistant and nice.
"""

from mido import MidiFile
from mido import MidiTrack

import tkinter as tk
from tkinter import filedialog


def getMidiFile():
    file = filedialog.askopenfilename(
        filetypes=[("Midi Files", "*.mid;*.midi"), ("All types", "*.*")],
        title="Source File",
    )
    if file == "":
        print("No file presented, closing...")
        exit(0)
    return file


def find_tempo_track(midi: MidiFile):
    total_tracks = len(midi.tracks)
    track_no = 0
    for t in range(total_tracks):
        track = midi.tracks[track_no]
        track_has_tempo = False
        for i in range(len(track)):
            event = track[i]
            match event.type:
                case "set_tempo":
                    track_has_tempo = True
                    break
        if track_has_tempo:
            break
        else:
            track_no += 1
    return track_no


def find_notes_track(midi: MidiFile):
    total_tracks = len(midi.tracks)
    track_no = 0
    note_track_no = ""
    for t in range(total_tracks):
        track = midi.tracks[track_no]
        track_has_notes = False
        for i in range(len(track)):
            event = track[i]
            match event.type:
                case "note_on" | "note_off":
                    track_has_notes = True
                    break
        if track_has_notes:
            note_track_no = track_no
            break
        else:
            track_no += 1
    return note_track_no
