"""
This script does the following:
- Removes the empty track FL creates and merges the tempo track with another track, allowing 16 channels to be used.
- Multiplies all pitch values by 6 so they sound the same as in FL
- Converts velocity and volume events to the DK64 linear curve (as opposed to FL's exponential curve)
  - this probably needs more fine tuning
- Removes unrecognized MIDI events
- Deletes duplicate patch events caused by fl
  - This also condenses the subsequent events on the same tick caused by patch changes.
  - This means that fl midis no longer need to be offset or have events at the loop to fix the patch bug!!
"""

from mido import MidiFile
from mido import MidiTrack
from mido import Message
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

valid_CCs = {
    "volume": 7,
    "reverb": 91,
    "pan": 10,
}


def remove_empty_track(midi: MidiFile):
    del midi.tracks[0]


def find_insertion_point(target_track: MidiTrack, total_tempo_time: int):
    total_target_time = 0
    for index in range(len(target_track)):
        total_target_time += target_track[index].time
        if total_target_time > total_tempo_time:
            return index, total_target_time
    return len(target_track), total_target_time


def move_tempo(midi: MidiFile):
    tempo_track = midi.tracks[0]
    target_track = midi.tracks[1]
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


def multiply_pitch(pitch: int):
    new_pitch = pitch * 6
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


def fix_pitch_and_volumes(midi: MidiFile, todo: str):
    for track in midi.tracks:
        for msg in track:
            match todo:
                case "both":
                    match msg.type:
                        case "pitchwheel":
                            msg.pitch = multiply_pitch(msg.pitch)
                        case "note_on":
                            msg.velocity = get_adjusted_volume(msg.velocity)  ###
                        case "control_change":
                            if msg.control == valid_CCs["volume"]:
                                msg.value = get_adjusted_volume(msg.value)

                case "volume":
                    match msg.type:
                        case "note_on":
                            msg.velocity = get_adjusted_volume(msg.velocity)  ###
                        case "control_change":
                            if msg.control == valid_CCs["volume"]:
                                msg.value = get_adjusted_volume(msg.value)

                case "pitch":
                    match msg.type:
                        case "pitchwheel":
                            msg.pitch = multiply_pitch(msg.pitch)


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


# Below, unsegmented, function by GlitchGlider! :3
# I'll clean it up and segment it at some point...


def fix_program_changes(midi: MidiFile):
    track_number = 0

    print("Track #\tPrev. Events\tDifference\tCurrent Events")

    for track in midi.tracks:
        track_number += 1
        filtered_program_msg_times = []
        all_msgs = []
        filtered_program_msgs = []
        track_messages_less = []
        track_messages_equal = []
        track_messages_more = []
        current_msg_time = 0
        patch_event_time = 0
        total_time = 0

        # Scan for all program change events and document their time/exact tick, not documenting duplicates.
        for i in range(len(track)):
            msg = track[i]
            total_time += msg.time
            if msg.type == "program_change":
                if total_time not in filtered_program_msg_times:
                    filtered_program_msg_times.append(total_time)
                    filtered_program_msgs.append(msg)

        events = len(track)
        # print("Track " + str(track_number) + " had " + str(len(track)) + " events.")

        if len(filtered_program_msgs) > 0:
            # Scan tick for all pan, pitch, & vol events in individual loops.

            # loop for each program event to filter everything before and after
            for i in range(len(filtered_program_msgs)):
                program_msg = filtered_program_msgs[i]
                all_msg_times = []
                current_msg_time = 0
                patch_event_time = 0
                prgm_has_reverb = False
                all_msgs.clear()
                track_messages_equal.clear()
                track_messages_less.clear()
                track_messages_more.clear()

                # inividual loop for each event to classify it
                for m in range(len(track)):
                    msg = track[m]
                    all_msgs.append(msg)
                    current_msg_time += msg.time
                    all_msg_times.append(current_msg_time)
                    msg.time = all_msg_times[m] - all_msg_times[m - 1]

                    if current_msg_time < filtered_program_msg_times[i]:
                        track_messages_less.append(msg)

                    elif current_msg_time > filtered_program_msg_times[i]:
                        track_messages_more.append(msg)

                    else:
                        match msg.type:

                            # Save the patch value
                            case "program_change":
                                program_instrument = msg.program
                                patch_event_time += msg.time

                            # Compare every event to the default value of that event and discard defaults.
                            # Save a unique value to a variable or use the default if there is none.
                            # saves time detla for all events that get scrapped on this tick for offsetting later
                            case "control_change":
                                if msg.control == valid_CCs["volume"]:
                                    chnl_vol = msg.value
                                    patch_event_time += msg.time
                                elif msg.control == valid_CCs["pan"]:
                                    chnl_pan = msg.value
                                    patch_event_time += msg.time
                                elif msg.control == valid_CCs["reverb"]:
                                    if msg.value != 0:
                                        chnl_verb = msg.value
                                        patch_event_time += msg.time
                                        prgm_has_reverb = True

                                else:
                                    track_messages_equal.append(msg)

                            case "pitchwheel":
                                chnl_pitch = msg.pitch
                                patch_event_time += msg.time

                            # Save other messages like note on/off, tempo & invalid ccs.
                            case _:
                                track_messages_equal.append(msg)

                # Once all values have been logged, delete all patch related events on that tick and just make a new one with the saved values.
                if filtered_program_msg_times[i] != total_time:
                    track_messages_equal.insert(
                        0,
                        Message(
                            "program_change",
                            channel=program_msg.channel,
                            time=patch_event_time,
                            program=program_instrument,
                        ),
                    )

                    track_messages_equal.insert(
                        1,
                        Message(
                            "control_change",
                            channel=program_msg.channel,
                            time=0,
                            control=valid_CCs["volume"],
                            value=chnl_vol,
                        ),
                    )

                    track_messages_equal.insert(
                        2,
                        Message(
                            "control_change",
                            channel=program_msg.channel,
                            time=0,
                            control=valid_CCs["pan"],
                            value=chnl_pan,
                        ),
                    )

                    track_messages_equal.insert(
                        3,
                        Message(
                            "pitchwheel",
                            channel=program_msg.channel,
                            time=0,
                            pitch=chnl_pitch,
                        ),
                    )

                    if prgm_has_reverb:
                        track_messages_equal.insert(
                            4,
                            Message(
                                "control_change",
                                channel=program_msg.channel,
                                time=0,
                                control=valid_CCs["reverb"],
                                value=chnl_verb,
                            ),
                        )

                # appends event lists to the track
                all_msgs.clear()
                all_msgs = (
                    track_messages_less + track_messages_equal + track_messages_more
                )
                track[:] = all_msgs

            print(
                str(track_number)
                + "\t"
                + str(events)
                + "\t\t"
                + str(len(track) - events)
                + "\t\t"
                + str(len(track))
            )
        else:
            print(str(track_number) + "\tEmpty Track")
    print("")


def clean_midi(midi_file: str):
    midi = MidiFile(midi_file)
    print("\n" + midi_file + "\n")
    remove_empty_track(midi)
    move_tempo(midi)
    fix_pitch_and_volumes(midi, "both")  # pitch, volume, or both
    remove_unrecognized_messages(midi)
    fix_program_changes(midi)
    midi.save(midi_file.replace(".mid", "_adjusted.mid"))


clean_midi(filedialog.askopenfilename())
