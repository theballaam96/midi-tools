"""
Version 1.2.0

- This script checks a MIDI file to see if there are any overlapping notes: Two note_on events of the same note in succession without a note_off between.

"""

from mido import MidiFile

from small_libs.dk64_data import DK64_INSTRUMENT_LIST
from small_libs.notes import get_note_name, set_sharp_or_flat
from small_libs.common import getMidiFile


# process MIDI messages
def check_overlap(input_midi: MidiFile, sub_func: bool):
    """
    Checks for overlapping notes and prints instances of such.
    :params:
        `input_midi`: the MidiFile object to search through.
        `sub_func`: a combo bool for usage of this function in another file without extra printing, pausing, ect.
    """

    active_notes = (
        []
    )  # stores which note is being held when iterating through each event
    numerator = 4  # default, will be read from the file
    has_overlapping = False
    track_name = None

    for track_index, original_track in enumerate(input_midi.tracks):

        current_instrument = ""  # contains the name of the current dk64 instrument
        absolute_ticks = 0  # contains the current time when processing each event

        for msg_index, msg in enumerate(original_track):

            absolute_ticks += msg.time

            if (
                (msg.type == "note_off")
                or (msg.type == "note_on" and msg.velocity == 0)
            ) and msg.note in active_notes:
                active_notes.remove(msg.note)

            else:
                match msg.type:
                    case "note_on":
                        if msg.note in active_notes:
                            print(
                                f'Overlapping note!{"":9s}{get_note_name(msg.note):11s}'
                                f'Bar: {round(absolute_ticks / input_midi.ticks_per_beat / numerator + 1, 2):>6.2f}{"":9s}'
                                f'Tick: {absolute_ticks:>6d}{"":9s}'
                                f'Channel {msg.channel:<2d}{"":9s}'
                                f'{track_name if track_name is not None else f"Track {track_index}"}: {current_instrument}'
                            )

                            next_msg = original_track[msg_index + 1]
                            if next_msg.type == "note_off" and next_msg.note == msg.note and next_msg.time == 0:
                                print("Listed overlap is 0 ticks long so no action is needed")
                            
                            has_overlapping = True
                        else:
                            active_notes.append(msg.note)

                    case "program_change":
                        if msg.program >= 95:
                            current_instrument = f"Non-DK64 Instrument: {msg.program}"
                        else:
                            current_instrument = DK64_INSTRUMENT_LIST[msg.program]

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
    set_sharp_or_flat("sharp")
    check_overlap(getMidiFile(), False)


if __name__ == "__main__":
    main()