from mido import MidiFile, MidiTrack, Message, MetaMessage, merge_tracks
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

def find_correct_track(detected_programs: dict, current_program: int) -> int:
    """Reverse lookup to find the current track number."""
    for j in range(len(detected_programs)): # iterate through the currectly known programs
        if detected_programs.get(j+1) == current_program: # until it finds the track with the correct program value
            return j+1
    return 0 # if no match is found, toss it in the first track along with tempo

def search_dict(global_detected_programs: dict) -> dict:
    """Searches global_detected_programs for entries with matching values and returns a dict of the matches."""
    matching_tracks = {}
    
    # get the first listed key
    for i in range(len(global_detected_programs)):
        search_dict = global_detected_programs[i]
        if search_dict:
            search_keys = search_dict.keys()
            search_program = search_dict.get(list(search_keys)[0])
            matching_tracks = {i: list(search_dict)[0]} # midi: track
            break

    # iterate through the dictionaries, and log any that have the same value as the first
    compare_i = 0
    for compare_dict in global_detected_programs:
        for compare_key in compare_dict.keys():
            if search_program == compare_dict.get(compare_key):
                matching_tracks.update({compare_i: compare_key})
        compare_i += 1

    return matching_tracks

def cipher_key(matching_cipher: dict, current_program: int) -> int:
    """Surely theres a simpler way to do this"""
    for j in range(len(matching_cipher)):
        if matching_cipher.get(j) == current_program:
            return j

def unscramble(old_midi: MidiFile) -> MidiFile:
    """This attempts to sort a midi by seperating each detected program change into its own track."""
    midis_to_merge = []
    global_detected_programs = []
    ticksincelastevent = {0: 0} # {track number : ticks since the last event was placed in track}
    current_program = None
    for track in old_midi.tracks: # search through the midi for every message
        new_midi = MidiFile(type=1, ticks_per_beat=old_midi.ticks_per_beat, tracks=[MidiTrack()])
        totaltrackticks = 0
        per_detected_programs = {} # {track number : correlating program number}
        i = 1
        for msg in track:
            match msg.type:
                case "program_change":
                    current_program = msg.program # change current program to this
                    if current_program not in per_detected_programs.values(): # check if this program has been seen before
                        per_detected_programs[i] = msg.program
                        ticksincelastevent.update({i: totaltrackticks})
                        i += 1
                        new_midi.tracks.append(MidiTrack([])) # if not, make a new track for it, and add it to the list

                    n = find_correct_track(per_detected_programs, current_program)
                    new_midi.tracks[n].append(msg.copy(time=ticksincelastevent[n]+msg.time)) # then add the message to the corresponding track

                case "note_on" | "note_off" | "control_change": # add this to the track of the current program
                    n = find_correct_track(per_detected_programs, current_program)
                    new_midi.tracks[n].append(msg.copy(time=ticksincelastevent[n]+msg.time))

                case _:
                    if msg.type != "end_of_track":
                        new_midi.tracks[0].append(msg)
            totaltrackticks += msg.time

            # add the time attribute of the current message to every track except the current one, which gets reset to zero
            n = find_correct_track(per_detected_programs, current_program)
            for t in range(len(ticksincelastevent)):
                if t == n:
                    ticksincelastevent.update({n: 0})
                else:
                    ticksincelastevent[t] += msg.time
            
        # reset ticks for the next track, but keep the amount of tracks stored
        for t in range(len(ticksincelastevent)):
            ticksincelastevent[t] = 0
        
        # add the assembled midis and detected to a list to be merged together later
        global_detected_programs.append(per_detected_programs)
        midis_to_merge.append(new_midi)


    merged_midi = midis_to_merge[0] # make a new midi which inherits the first track, since that should just have setup stuff
    global_detected_programs.pop(0) # and since the first track shouldn't have programs, just remove the first entry
    while True: # repeat until global_detected_programs is empty
        matching_cipher = search_dict(global_detected_programs)

        # add the corresponding track from global_detected_programs to the merge queue
        tracks_to_merge = []
        for i in matching_cipher.keys():
            tracks_to_merge.append(midis_to_merge[i+1].tracks[matching_cipher.get(i)])

        h = merge_tracks(tracks_to_merge)
        merged_midi.tracks.append(h)

        # remove the entries that have been combined, to be searched again
        for i in matching_cipher.keys():
            global_detected_programs[i].pop(matching_cipher.get(i))
        
        for i in range(len(global_detected_programs)): # checks if global_detected_programs is empty
            if not global_detected_programs[i]:
                continue # if the entry is empty, check the next one
            else:
                break # if anything is detected, the list is not empty and you should keep going
        else:
            break # if all entries pass, the list must be empty so break the while loop
    
    # last step, organise the channels of the midi so SynthFont doesn't split the channels
    completed_midi = MidiFile(type=1, ticks_per_beat=old_midi.ticks_per_beat, tracks=[])
    i = 0
    c = 0
    for track in merged_midi.tracks:
        completed_midi.tracks.append(MidiTrack())
        for msg in track:
            match msg.type:
                case "note_on" | "note_off" | "program_change" | "control_change":
                    completed_midi.tracks[i].append(msg.copy(channel=c))
                case _:
                    completed_midi.tracks[i].append(msg.copy())
        if c < 15:
            c += 1
        else:
            c = 0
        i += 1
    return completed_midi
    

def clean_midi(midi_file: str):
    old_midi = MidiFile(midi_file)
    if old_midi.type == 0:
        raise TypeError("MIDI must be type 1")
    print("\n" + midi_file + "\n")
    new_midi = unscramble(old_midi)
    new_midi.save(midi_file.replace(".mid", "_sorted.mid"))

clean_midi(filedialog.askopenfilename())