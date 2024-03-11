import mido
import os
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

OLD_MIDI = filedialog.askopenfilename()
NEW_MIDI = OLD_MIDI.replace(".mid","_converted.mid")

def convert_type0_type1(midi_type0_file):
    type_0 = mido.MidiFile(midi_type0_file)
    if type_0.type != 0:
        return
    type_1 = mido.MidiFile(
        type=1,
        ticks_per_beat=type_0.ticks_per_beat)
    time = 0
    channels = {}
    for item in type_0.tracks[0]:
        msg = item.copy()

        if hasattr(msg, 'time'):
            time += msg.time

        channel = msg.channel if hasattr(msg, 'channel') else -1
        if channel not in channels:
            channels[channel] = {
                'time': 0,
                'msg': []
            }
        chl = channels[channel]

        if hasattr(msg, 'time'):
            msg.time = time - chl['time']
            chl['time'] = time
        chl['msg'].append(msg)

    for chan in channels:
        track = type_1.add_track()
        track.extend(channels[chan]['msg'])

    type_1.save(NEW_MIDI)

convert_type0_type1(OLD_MIDI)