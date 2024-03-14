'''
This script does the following:
- Removes the empty track FL creates (so you can have 15 channels)
- Multiplies all pitch values by 6 so they sound the same as in FL
- Converts velocity and volume events to the DK64 linear curve (as opposed to FL's exponential curve)
Note: this probably needs more fine tuning
- Removes MIDI events/messages that DK64 will not use or recognize
'''

from mido import MidiFile
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

valid_CCs = {
    "volume" : 7,
    "reverb" : 91,
    "pan" : 10,
}

def remove_empty_track(midi: MidiFile):
    del midi.tracks[0]

def multiply_pitch(pitch: int):
    new_pitch = pitch * 6
    clamped_pitch = max(min(8191, new_pitch),-8192)
    return clamped_pitch

def get_expected_FL_volume(velocity: int):
    #.62 / 127 ^ 2 * x ^ 2, max = .62
    #.002
    #x + .01, max = .264
    return (.62 / (127 ** 2)) * (velocity ** 2)

def DK_volume_to_approx_velocity(volume: float):
    #y = .002
    #x + 0.1
    #x = (y / .002)
    approx_velocity = max(0, volume / .002078);
    approx_velocity = min(127, approx_velocity);
    return round(approx_velocity)

def get_adjusted_volume(velocity: int):
    maxFL = .620
    maxDK = .264
    expected_FL_volume = get_expected_FL_volume(velocity)
    expected_FL_percent = expected_FL_volume / maxFL
    DK_volume = maxDK * expected_FL_percent
    adjusted_velocity = DK_volume_to_approx_velocity(DK_volume)
    return adjusted_velocity

def fix_pitch_and_volumes(midi: MidiFile):
    for track in midi.tracks:
        for msg in track:
            match msg.type:
                case 'pitchwheel':
                    msg.pitch = multiply_pitch(msg.pitch)
                case 'note_on':
                    msg.velocity = get_adjusted_volume(msg.velocity)
                case 'control_change':
                    if msg.control == valid_CCs["volume"]:
                        msg.value = get_adjusted_volume(msg.value)

def remove_unrecognized_messages(midi: MidiFile):
    accepted_messages = ["note_off","note_on","control_change","program_change","pitchwheel"]
    for track in midi.tracks:
        filtered_messages = []
        for msg in track:
            if msg.is_meta:
                filtered_messages.append(msg)
            elif msg.type in accepted_messages:
                if msg.type != "control_change":
                    filtered_messages.append(msg)
                else:
                    if msg.control in valid_CCs.values():
                        filtered_messages.append(msg)
        track[:] = filtered_messages

def clean_midi(midi_file: str):
    midi = MidiFile(midi_file)
    remove_empty_track(midi)
    fix_pitch_and_volumes(midi)
    remove_unrecognized_messages(midi)
    midi.save(midi_file.replace(".mid","_adjusted.mid"))

clean_midi(filedialog.askopenfilename())