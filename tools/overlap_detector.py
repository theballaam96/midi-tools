"""
Version 1.0.1

- This script checks a MIDI file to see if there are any overlapping notes: a note on event when the last note wasn't closed.

"""

import math
from mido import MidiFile, tick2second
import tkinter as tk
from tkinter import filedialog

import small_libs.dk64_data as dk64data
import small_libs.notes as note_names

root = tk.Tk()
root.withdraw()


# process MIDI messages
def check_overlap(input_midi: str, sub_func: bool):
    """
    Checks for overlapping notes and prints instances of such.
    sub_func is a combo bool for usage of this function in another file without extra printing, pausing, ect.
    """

    notes = {}  # stores which note is being held when iterating through each event
    numerator = 4  # default, will be read from the file
    has_overlapping = False
    track_name = None

    for original_track in input_midi.tracks:

        current_instrument = ""  # contains the name of the current dk64 instrument
        absolute_ticks = 0  # contains the current time when processing each event

        for msg in original_track:

            absolute_ticks += msg.time

            if (msg.type == "note_off") or (
                msg.type == "note_on" and msg.velocity == 0
            ):

                try:
                    del notes[msg.note]
                except Exception:
                    print(f"Something went wrong trying to delete note at tick {absolute_ticks} in channel {current_instrument}")

            else:
                match msg.type:
                    case "note_on":
                        if msg.note in notes:
                            print(
                                f'Overlapping note!{"":9s}{note_names.get_note_name(msg.note):11s}Bar: {round(absolute_ticks / input_midi.ticks_per_beat / numerator + 1, 2):>6.2f}{"":9s}Tick: {absolute_ticks:>6d}{"":9s}Channel {msg.channel:<2d}{"":9s}"{track_name}" : {current_instrument}'
                            )
                            has_overlapping = True
                        notes[msg.note] = msg

                    case "program_change":
                        current_instrument = dk64data.dk64_instrument_list[msg.program]

                    case "time_signature":
                        numerator = msg.numerator

                    case "track_name":
                        track_name = msg.name

    if has_overlapping:
        print("\nThere are overlapping notes in this file!\n")

    elif (not has_overlapping) and (not sub_func):
        print("There are not overlapping notes in this file.\n")

    if (not sub_func) or has_overlapping:
        input("Press enter to close...")


def main():

    note_names.set_sharp_or_flat("sharp")  # 'sharp' or 'flat'
    check_overlap(MidiFile(filedialog.askopenfilename()), False)


if __name__ == "__main__":
    main()
