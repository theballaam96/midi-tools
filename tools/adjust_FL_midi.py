"""
Version 1.1.1

This script does the following:
- Removes the empty tracks FL creates and merges the tempo track with another track, allowing 16 channels to be used.
- Multiplies all pitch values by 6 so they sound the same as in FL
  - or alternativly multiplies to the proper instrument bend range. (see dk64_data.py for instrument ranges)
- Converts velocity and volume events to the DK64 linear curve (as opposed to FL's exponential curve)
  - The max volume of FL has to be adjusted by the user to compensate for DK64's max volume.
- Removes unrecognized MIDI events
- Deletes duplicate patch events caused by fl
  - This also condenses the subsequent events on the same tick caused by patch changes.
  - This means that fl midis no longer need to be offset or have events at the loop to fix the patch bug!!
- Calls the overlap detector at the end, for convenience.
"""

from mido import MidiFile
from mido import MidiTrack
from mido import Message
import tkinter as tk
from tkinter import filedialog

import small_libs.dk64_data as dk64data
import small_libs.notes as note_names
import fix_patch_events as patcher
import small_libs.common as common

from overlap_detector import check_overlap

root = tk.Tk()
root.withdraw()

valid_CCs = {
    "volume": 7,
    "reverb": 91,
    "pan": 10,
}


def remove_empty_tracks(midi: MidiFile):
    total_tracks = len(midi.tracks)
    track_no = 0
    for t in range(total_tracks):
        track = midi.tracks[track_no]
        track_is_good = False
        for i in range(len(track)):
            event = track[i]
            match event.type:
                case "note_on" | "note_off" | "set_tempo":
                    track_is_good = True
                    break
        if not track_is_good:
            del midi.tracks[track_no]
        else:
            track_no += 1


def find_insertion_point(target_track: MidiTrack, total_tempo_time: int):
    total_target_time = 0
    for index in range(len(target_track)):
        total_target_time += target_track[index].time
        if total_target_time > total_tempo_time:
            return index, total_target_time
    return len(target_track), total_target_time


def move_tempo(midi: MidiFile):
    tempo_track = midi.tracks[common.find_tempo_track(midi)]
    target_track = common.find_notes_track(midi)
    if target_track == "":
        input("ERROR: This file is empty; nowhere to place tempo...")
        exit(1)
    else:
        target_track = midi.tracks[target_track]
    tempo_msgs = [msg for msg in tempo_track if msg.type == "set_tempo"]
    total_tempo_time = 0
    for tempo_msg in tempo_msgs:
        total_tempo_time += tempo_msg.time
        insertion_point, total_target_time = find_insertion_point(
            target_track, total_tempo_time
        )
        if insertion_point == len(target_track):
            tempo_msg.time = total_tempo_time - total_target_time
        else:
            current_msg = target_track[insertion_point]
            previous_total_time = total_target_time - current_msg.time
            new_inserted_time = total_tempo_time - previous_total_time
            tempo_msg.time = new_inserted_time
            target_track[insertion_point].time = total_target_time - total_tempo_time
        target_track.insert(insertion_point, tempo_msg)
    del midi.tracks[0]


def multiply_pitch(pitch: int, bend_range=2):
    new_pitch = int(pitch * (12 / bend_range))
    clamped_pitch = max(min(8191, new_pitch), -8192)
    return clamped_pitch


def get_expected_FL_volume(velocity: int):
    # .62 / 127 ^ 2 * x ^ 2, max = .62
    # .002
    # x + .01, max = .264
    return (0.62 / (127**2)) * (velocity**2)


def DK_volume_to_approx_velocity(volume: float):
    # y = .002
    # x + 0.1
    # x = (y / .002)
    approx_velocity = max(0, volume / 0.002078)
    approx_velocity = min(127, approx_velocity)
    return round(approx_velocity)


def get_adjusted_volume(velocity: int):
    maxFL = 0.620
    maxDK = 0.264
    expected_FL_volume = get_expected_FL_volume(velocity)
    expected_FL_percent = expected_FL_volume / maxFL
    DK_volume = maxDK * expected_FL_percent
    adjusted_velocity = DK_volume_to_approx_velocity(DK_volume)
    return adjusted_velocity


def adjust_events(midi: MidiFile, todo: list):
    """
    adjust_events does the following:
        adjusts the panning to, partially, match fl.
        adjusts pitch bends to the *appropriate range*
            range can either compensate fl's midi out /6 factor (normal),
            or adjust to the accurate instrument range (instrument)
        adjusts volume curve to match FL, when fl's max output is adjusted.

    options for this are: 'pitch-normal' or 'pitch-instrument', and 'volume'
    """
    for track in midi.tracks:
        instrument = 0
        for msg in track:
            match msg.type:
                case "program_change":
                    instrument = msg.program

                case "pitchwheel":
                    # the function simply
                    if ("pitch-normal" in todo) & ("pitch-instrument" not in todo):
                        msg.pitch = multiply_pitch(msg.pitch)

                    # calls the function to return the bend range and give that to the function to use
                    elif "pitch-instrument" in todo:
                        msg.pitch = multiply_pitch(
                            msg.pitch, dk64data.get_pitch_range(instrument)
                        )

                case "note_on":
                    if "volume" in todo:
                        msg.velocity = get_adjusted_volume(msg.velocity)

                case "control_change":
                    if msg.control == valid_CCs["volume"]:
                        if "volume" in todo:
                            msg.value = get_adjusted_volume(msg.value)

                    """
                    Do this later
                    
                    elif msg.control == valicd_CCs["panning"]:
                        if "panning" in todo:
                            msg.value = get_adjusted_panning()"""


def remove_unrecognized_messages(midi: MidiFile):
    accepted_messages = [
        "note_off",
        "note_on",
        "control_change",
        "program_change",
        "pitchwheel",
    ]
    for track in midi.tracks:
        filtered_messages = []
        for i in range(len(track)):
            msg = track[i]
            good = False
            if msg.is_meta:
                good = True
            elif msg.type in accepted_messages:
                if msg.type != "control_change":
                    good = True
                else:
                    if msg.control in valid_CCs.values():
                        good = True
            if good:
                filtered_messages.append(msg)
            else:
                if i < len(track) - 1:
                    track[i + 1].time += msg.time
        track[:] = filtered_messages


#


def clean_midi(midi_file: str):

    midi = MidiFile(midi_file)
    print("\n" + midi_file + "\n")

    remove_empty_tracks(midi)
    move_tempo(midi)

    """
    adjust_events does the following:
        adjusts the panning to, partially, match fl.
        adjusts pitch bends to the *appropriate range*
            range can either compensate fl's midi out /6 factor (normal),
            or adjust to the accurate instrument range (instrument)
        adjusts volume curve to match FL, when fl's max output is adjusted.

    options for this are: 'pitch-normal' or 'pitch-instrument', and 'volume' """
    adjust_events(midi, ["pitch-normal", "volume"])
    remove_unrecognized_messages(midi)

    patcher.fix_program_changes(midi)

    # sets note names names to 'sharp' or 'flat', then checks for overlapping notes
    note_names.set_sharp_or_flat("sharp")
    check_overlap(midi, True)

    # saves file with '_adjusted' added to the filename
    midi.save(midi_file.replace(".mid", "_adjusted.mid"))


if __name__ == "__main__":
    clean_midi(common.getMidiFile())
