"""
Version 1.0.1

- This script checks a MIDI file to see if there are any instances if too many notes playing at once, breakingDK64's engine.
"""

from mido import MidiFile

from small_libs.dk64_data import REVERB_TAIL, MAX_VOICES, get_instrument_release
from small_libs.notes import set_sharp_or_flat
from small_libs.common import getMidiFile


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
def check_voices(input_midi: MidiFile, sub_func: bool):
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
                    (get_instrument_release(instrument) / tempo)
                    * input_midi.ticks_per_beat
                )
                if reverb:
                    note_release_ticks = round(
                        (REVERB_TAIL / tempo) * input_midi.ticks_per_beat
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
        if (active_voices > MAX_VOICES) and not sub_func:
            print(
                f'{active_voices} Voices{"":9s}Bar: {round(absolute_ticks / input_midi.ticks_per_beat / numerator + 1, 2):>6.2f}{"":6s}Tick: {absolute_ticks:>6d}'
            )

    if peak_voices <= MAX_VOICES:
        print(
            f"\nThe voices only reached a peak of {peak_voices} out of {MAX_VOICES} availible!\n"
        )
    else:
        print(
            f"\nThe voices hit a peak of {peak_voices} out of {MAX_VOICES} availible!\nThis will need to be fixed or notes will be dropped in game!\n"
        )

    if not sub_func:
        input("Press enter to close...")


def main():
    set_sharp_or_flat("sharp")
    check_voices(getMidiFile(), False)


if __name__ == "__main__":
    main()
