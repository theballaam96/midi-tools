"""
Version 0.9

This script reads midi data back out to you
"""

from mido import MidiFile
from mido import MidiTrack
import tkinter as tk
from tkinter import filedialog
from mido import tempo2bpm

import small_libs.dk64_data as dk64data
import small_libs.notes as notes

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


def read_msg_data(track_data: list):
    """
    reads a single MidiTrack and prints it to the console.
    """

    temp_instrument = 0  # the numerical value of the current instrument called for calculating pitch bend ranges
    time = 0  # true time for printing
    active_notes = []  # active notes for detecting overlaps in this file too!

    for i in range(len(track_data)):

        msg = track_data[i]
        time += msg.time

        match msg.type:
            case "note_on":
                if msg.velocity == 0:

                    if msg.note in active_notes:
                        active_notes.remove(msg.note)

                    print(
                        f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                        f"{'Note Off':28s}{notes.get_note_name(msg.note):<28s}0"
                    )

                else:
                    if msg.note in active_notes:
                        print(
                            f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                            f"{'Note Overlap!':28s}{notes.get_note_name(msg.note):<28s}{msg.velocity}"
                        )
                    else:
                        active_notes.append(msg.note)

                    print(
                        f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                        f"{'Note On':28s}{notes.get_note_name(msg.note):<28s}{msg.velocity}"
                    )

            case "note_off":
                if msg.note in active_notes:
                    active_notes.remove(msg.note)

                print(
                    f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                    f"{'Note Off':28s}{notes.get_note_name(msg.note)}"
                )

            case "control_change":
                if msg.control in cc_to_name:
                    control_type = cc_to_name[msg.control]
                    match control_type:
                        case "Reverb":
                            print(
                                f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                                f"{'Control Change':28s}{'Reverb':28s}{round(msg.value / 1.27, 2)}%"
                            )
                        case "Panning":
                            if msg.value < 64:
                                print(
                                    f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                                    f"{'Control Change':28s}{'Panning':28s}{(-msg.value + 64)}/64 Left"
                                )
                            elif msg.value > 64:
                                print(
                                    f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                                    f"{'Control Change':28s}{'Panning':28s}{(msg.value - 64)}/63 Right"
                                )
                            else:
                                print(
                                    f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                                    f"{'Control Change':28s}{'Panning':28s}Centered"
                                )
                        case _:
                            print(
                                f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                                f"{'Control Change':28s}{control_type:28s}{msg.value}"
                            )
                else:
                    print(
                        f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                        f"{'Control Change':28s}CC #{msg.control:24d}{msg.value}"
                    )

            case "program_change":
                temp_instrument = msg.program
                if msg.program < 94:
                    print(
                        f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                        f"{'Program Change':28s}{dk64data.dk64_instrument_list[msg.program]:28s}{msg.program}"
                    )
                else:
                    print(
                        f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                        f"{'Program Change':28s}{msg.program:<28d}N/A"
                    )

            case "pitchwheel":
                if msg.pitch < 0:
                    print(
                        f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                        f"{'Control Change':28s}{'Pitch':27s}-{round(((-msg.pitch) / 8192)* dk64data.get_pitch_range(temp_instrument), 2)} ST"
                    )
                elif msg.pitch > 0:
                    print(
                        f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                        f"{'Control Change':28s}{'Pitch':27s}+{round(((msg.pitch) / 8191)* dk64data.get_pitch_range(temp_instrument), 2)} ST"
                    )
                else:
                    print(
                        f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                        f"{'Control Change':28s}{'Pitch':28s}0 ST"
                    )

            case "aftertouch":
                print(
                    f"{time:<8d} Ch. {msg.channel:>2d}{'':4s}"
                    f"{'Control Change':28s}{'Aftertouch':28s}{msg.value}"
                )

            case "track_name":
                print(f"{time:<8d} {'Meta':<10s}{'Track Name':27s}\"{msg.name}\"")

            case "set_tempo":
                print(
                    f"{time:<8d} {'Meta':<10s}{'Tempo Change':28s}{round(tempo2bpm(msg.tempo), 3)}"
                )

            case "end_of_track":
                print(f"{time:<8d} {'Meta':<10s}End of Track")

            case "sequence_number":
                print(f"{time:<8d} {'Meta':<10s}{'Sequence Number':28s}{msg.number}")

            case "time_signature":
                print(
                    f"{time:<8d} {'Meta':<10s}{'Time Signature':28s}{msg.numerator}/{msg.denominator}"
                )

            case "key_signature":
                print(f"{time:<8d} {'Meta':<10s}{'Key Signature':28s}{msg.key}")

            case "channel_prefix":
                print(f"{time:<8d} {'Meta':<10s}Channel Prefix")

            case "instrument_name":
                print(f"{time:<8d} {'Meta':<10s}{'Instrument Name':28s}{msg.name}")

            case "midi_port":
                print(f"{time:<8d} {'Meta':<10s}{'Midi Port':28s}{msg.port}")

            case "marker":
                print(f"{time:<8d} {'Meta':<10s}{'Marker':28s}\"{msg.text}\"")

            case "text":
                print(f"{time:<8d} {'Meta':<10s}{'Text':28s}\"{msg.text}\"")

            case "smpte_offset":
                print(
                    f"{time:<8d} {'Meta':<10s}{'SMPTE Offset':28s}{msg.hours:02d}:{msg.minutes:02d}:{msg.seconds:02d}:{int((msg.frames / msg.frame_rate) * 100):02d}"
                )

            case "sysex":
                print(
                    f"{time:<8d} {'Meta':<10s}SysEx Message\n{'':<9s}{'':=<10s}{msg.data}"
                )

            case "copyright":
                print(f"{time:<8d} {'Meta':<10s}{'Copyright':28s}\"{msg.text}\"")

            case _:
                print(
                    f"{time:<8d} {'Meta':<10s}Unknown Message\n{'':<9s}{'':=<10s}{msg}"
                )

    print(f"\n{len(track_data)} events\n\n")


def read_midi_data(midi: MidiFile):
    track_number = 0
    for track in midi.tracks:
        print(f"\n= Track {track_number + 1} =\n")
        read_msg_data(track)
        track_number += 1


def read_single_track(midi: MidiFile, track_id):
    track_number = track_id - 1
    track = midi.tracks[track_number]
    read_msg_data(track)


#


def read_midi(midi_file: str):
    midi = MidiFile(midi_file)
    notes.set_sharp_or_flat("sharp")  # 'sharp' or 'flat'
    read_midi_data(midi)
    # read_single_track(midi, 1)  # Track number 1-16 or 1-18 before FL fixing
    input("Press enter to close...")


read_midi(filedialog.askopenfilename())
