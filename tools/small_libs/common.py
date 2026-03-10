"""
Common functions to reuse in most files, just to make starting seperate files more consistant and nice.
"""

from mido import MidiFile, MidiTrack
from tkinter import filedialog


def getMidiFile(**kwargs):
    """
    Prompts the user for a midi file and returns a MidiFile object of that file.
    :params: 
        `path`: `Optional[bool]`. If True, will also return the prompted file's path as a string.
        `title`: `Optional[str]` the title for the tkinter dialog box.
    """
    file = filedialog.askopenfilename(
        filetypes=[("Midi Files", "*.mid;*.midi"), ("All types", "*.*")],
        title=kwargs["title"] if "title" in kwargs else "Source File",
    )
    if file == "":
        print("No file presented, closing...")
        exit(0)
    if "path" in kwargs:
        if kwargs["path"]:
            return MidiFile(file), file
    return MidiFile(file)


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
