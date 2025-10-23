"""
Version 1.1.2


- Deletes duplicate patch events caused by fl
  - This also condenses the subsequent events on the same tick caused by patch changes.
  - This means that fl midis no longer need to be offset or have events at the loop to fix the patch bug!!
"""

from tkinter import filedialog

from mido import MidiFile
from mido import Message
import small_libs.common as common

valid_CCs = {
    "volume": 7,
    "reverb": 91,
    "pan": 10,
}


def fix_program_changes(midi: MidiFile):
    """
    Huge function that runs through each track in an input midi file, documents all the program changes per track.

    Then runs through all the program changes, saves values to carry over.
        Then replaces the program change(s) on that tick with a new one and it's subsiquent cc events.
    """

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

        events_qty = len(track)
        # print(f"Track {track_number} had {len(track)} events.")

        if len(filtered_program_msgs) > 0:
            # Scan tick for all pan, pitch, & vol events in individual loops.

            # loop for each program event to filter everything before and after
            for i in range(len(filtered_program_msgs)):
                program_msg = filtered_program_msgs[i]
                all_msg_times = []
                final_msg_times = []
                current_msg_time = 0
                patch_event_time = 0
                all_msgs.clear()
                track_messages_equal.clear()
                track_messages_less.clear()
                track_messages_more.clear()
                prgm_has_pitch = False
                prgm_has_reverb = False
                previous_pitch = 0
                previous_reverb = 0
                chnl_vol = 127
                chnl_pan = 64

                # inividual loop for each event to classify it
                for m in range(len(track)):
                    msg = track[m]
                    all_msgs.append(msg)
                    current_msg_time += msg.time
                    all_msg_times.append(current_msg_time)
                    msg.time = all_msg_times[m] - all_msg_times[m - 1]

                    # events that take place before the current patch being fixed
                    if current_msg_time < filtered_program_msg_times[i]:
                        final_msg_times.append(current_msg_time)
                        track_messages_less.append(msg)
                        match msg.type:
                            case "control_change":
                                if msg.control == valid_CCs["reverb"]:
                                    previous_reverb = msg.value
                                if msg.control == valid_CCs["volume"]:
                                    chnl_vol = msg.value
                                if msg.control == valid_CCs["pan"]:
                                    chnl_pan = msg.value
                            case "pitchwheel":
                                previous_pitch = msg.pitch

                    # events that take place after the current patch being fixed
                    elif current_msg_time > filtered_program_msg_times[i]:
                        if msg.type == "end_of_track":
                            msg.time = total_time - final_msg_times[-1]
                        final_msg_times.append(current_msg_time)
                        track_messages_more.append(msg)

                    # events that take place on the same tick the current patch being fixed
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

                                # Volume and panning are reset on patch swap, so those are compared to the default values
                                if msg.control == valid_CCs["volume"]:
                                    patch_event_time += msg.time
                                    chnl_vol = msg.value
                                elif msg.control == valid_CCs["pan"]:
                                    patch_event_time += msg.time
                                    chnl_pan = msg.value

                                # Reverb and pitch do not get reset and will only change the value if it has changed
                                elif msg.control == valid_CCs["reverb"]:
                                    patch_event_time += msg.time
                                    if msg.value != previous_reverb:
                                        chnl_verb = msg.value
                                        previous_reverb = msg.value
                                        prgm_has_reverb = True

                                else:
                                    patch_event_time += msg.time
                                    msg.time = 0
                                    final_msg_times.append(current_msg_time)
                                    track_messages_equal.append(msg)

                            case "pitchwheel":
                                patch_event_time += msg.time
                                if msg.pitch != previous_pitch:
                                    chnl_pitch = msg.pitch
                                    previous_pitch = msg.pitch
                                    prgm_has_pitch = True

                            # for the end of the track's time to be preserved
                            case "end_of_track":
                                msg.time = total_time - final_msg_times[-1]
                                track_messages_equal.append(msg)

                            # Save other messages like note on/off, tempo & invalid ccs.
                            case _:
                                if not current_msg_time == total_time:
                                    patch_event_time += msg.time
                                    msg.time = 0
                                final_msg_times.append(current_msg_time)
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

                    if chnl_pan != 64:
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

                    if prgm_has_pitch:
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
                f"{track_number}\t{events_qty}\t\t{len(track) - events_qty}\t\t{len(track)}"
            )
        else:
            print(f"{track_number}\tEmpty Track")
    print()


#


def main(midi_file: str):
    midi = MidiFile(midi_file)
    fix_program_changes(midi)
    midi.save(midi_file.replace(".mid", "_patch_fixed.mid"))


if __name__ == "__main__":
    main(common.getMidiFile())
