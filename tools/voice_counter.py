"""
Version 1.0.0

- This script checks a MIDI file to see if there are any instances if too many notes playing at once, breakingDK64's engine.
"""

import math
from mido import MidiFile, tick2second
import tkinter as tk
from tkinter import filedialog

import small_libs.dk64_data as dk64data
import small_libs.notes as note_names
import small_libs.common as common

root = tk.Tk()
root.withdraw()


cc_to_name = {
    1: "Mod Wheel",
    5: "Portamento",
    6: "Data Entry",
    7: "Volume",
    10: "Panning",
    11: "Expression",
    91: "Reverb",
    100: "RPN 100",
    101: "RPN 101",
}


# process MIDI messages
def check_voices(input_midi: str, sub_func: bool):
    """
    Checks for voice count and prints if the max is reached.
    sub_func is a combo bool for usage of this function in another file without extra printing, pausing.
        sub_func off is also much more verbose if needed!
    """

    active_voices = 0  # stores how many voices there are.
    note_events = {}  # stores all note on/off events as a tick_time:incremental
    peak_voices = 0
    note_release_ticks = 0
    tempo = 0

    numerator = 4  # default, will be read from the file

    for original_track in input_midi.tracks:

        absolute_ticks = 0  # contains the current time when processing each event
        instrument = 0
        reverb = False

        for msg in original_track:

            absolute_ticks += msg.time

            if msg.type == "note_off":

                note_release_ticks = round(
                    (dk64data.get_instrument_release(instrument) / tempo)
                    * input_midi.ticks_per_beat
                )
                if reverb:
                    note_release_ticks = round(
                        (dk64data.reverb_tail / tempo) * input_midi.ticks_per_beat
                    )

                if (absolute_ticks + note_release_ticks) in note_events:
                    note_events[absolute_ticks + note_release_ticks] -= 1
                else:
                    note_events[absolute_ticks + note_release_ticks] = -1

            elif msg.type == "note_on":
                if absolute_ticks in note_events:
                    note_events[absolute_ticks] += 1
                else:
                    note_events[absolute_ticks] = 1

            elif msg.type == "time_signature":
                numerator = msg.numerator

            elif msg.type == "program_change":
                instrument = msg.program

            elif msg.type == "set_tempo":
                tempo = msg.tempo

            elif msg.type == "control_change":
                if cc_to_name[msg.control] == "Reverb" and msg.value > 0:
                    reverb = True

    all_times = sorted(note_events)
    for time in all_times:
        active_voices += note_events.get(time)
        peak_voices = max(peak_voices, active_voices)
        if (active_voices > dk64data.max_voices) and not sub_func:
            print(
                f'{active_voices} Voices{"":9s}Bar: {round(absolute_ticks / input_midi.ticks_per_beat / numerator + 1, 2):>6.2f}{"":6s}Tick: {absolute_ticks:>6d}'
            )

    if peak_voices <= dk64data.max_voices:
        print(
            f"\nThe voices only reached a peak of {peak_voices} out of {dk64data.max_voices} availible!\n"
        )
    else:
        print(
            f"\nThe voices hit a peak of {peak_voices} out of {dk64data.max_voices} availible!\nThis will need to be fixed or notes will be dropped in game!\n"
        )

    if not sub_func:
        input("Press enter to close...")


def main():

    note_names.set_sharp_or_flat("sharp")  # 'sharp' or 'flat'
    check_voices(MidiFile(common.getMidiFile()), False)


if __name__ == "__main__":
    main()
