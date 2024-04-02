# This script reads midi data back out to you


from mido import MidiFile
from mido import MidiTrack
import tkinter as tk
from tkinter import filedialog
from mido import tempo2bpm

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
dk64_instrument_list = [
    "N/A",
    "Marimba",
    "Rototom",
    "Taiko Drum",
    "Pan Flute",
    "Wood Scraper",
    "Shakers",
    "Woodblock",
    "Bongos",
    "Drum Kit",
    "Donkey Kong Vox",
    "Log Drum",
    "Misc Animal SFX",
    "Cricket SFX",
    "Saxophone",
    "Clarinet",
    "Trombone",
    "Trumpet",
    "Sustain Strings",
    "Shehnai",
    "Muted Trumpet",
    "Fretless Bass",
    "Xylophone",
    "Harp",
    "Music Box",
    "Gong",
    "Glockenspiel",
    "Theremin",
    "Water Glug SFX",
    "Timpani",
    "Tuba",
    "French Horn",
    "Bassoon",
    "Piccolo",
    "Snare & Snare Roll",
    "E-Bass",
    "Water Drop SFX",
    "Triangle",
    "Whistle",
    "Clavinet",
    "Choir (Ah)",
    "Wind SFX",
    "Timbale",
    "Harsh Handpan",
    "Electric Guitar",
    "Whispery Chant Vox",
    "Pizzicato Strings",
    "Snake Rattle",
    "Vibraslap",
    "Toy Wind-up & Noise SFX",
    "Trumpet Fall",
    "Synth Bass",
    "Brass Section",
    "Rock Organ",
    "Tonky Piano",
    "Drawbar Organ",
    "Muted Bass/Banjo",
    "Fingersnap",
    "Pizzicato Bass Strings",
    "Bat SFX",
    "Muted Trumpet (Vibrato)",
    "Clarinet (Vibrato)",
    "Rambi Scream SFX",
    "Maniacal Laugh Vox",
    "Staccato Strings",
    "Air Horn",
    "Computer SFX",
    "Production Room SFX",
    "White Noise",
    "Tubular Bells",
    "Seagull Loop SFX",
    "Tremolo Pad",
    "Crowd Noise SFX",
    "Bird & Bee SFX",
    "Banana Fairy Vox",
    "Owl & Wolf SFX",
    "Electric Guitar (Ext. PBend)",
    "Oh Banana Vox",
    "Hip Hop Drum Loop",
    "DK Rapper Vox",
    "DJ Vox & SFX",
    "Guitar Riffs",
    "Electric Guitar Riffs",
    "Tremolo High Strings",
    "Contrabassoon",
    "Harpsichord",
    "Creepy Laughter Vox",
    "Steel Drums",
    "Clanking Chain SFX",
    "Low Rumble SFX",
    "DK Radio Loop",
    "Yawns & Moans Vox",
    "Monkey SFX",
    "Concert Bass Drum",
    "Happy Laughters Vox",
]
note_names_sharp = [
    "C",
    "C\u266F",
    "D",
    "D\u266F",
    "E",
    "F",
    "F\u266F",
    "G",
    "G\u266F",
    "A",
    "A\u266F",
    "B",
]
note_names_flat = [
    "C",
    "D\u266D",
    "D",
    "E\u266D",
    "E",
    "F",
    "G\u266D",
    "G",
    "A\u266D",
    "A",
    "B\u266D",
    "B",
]


def get_note_name(note: int):
    if sharp_or_flat == "flat":
        note_name = str(note_names_flat[note % 12] + str(int(note / 12)))
    else:
        note_name = str(note_names_sharp[note % 12] + str(int(note / 12)))
    return note_name


def read_msg_data(track_data: list, track_id: int):
    time = 0
    for i in range(len(track_data)):
        msg = track_data[i]
        time += msg.time
        match msg.type:
            case "note_on":
                print(
                    str(time)
                    + "\tCh. "
                    + str(msg.channel)
                    + "\tNote On\t\t\t"
                    + get_note_name(msg.note)
                    + "\t\t\t"
                    + str(msg.velocity)
                )
            case "note_off":
                print(
                    str(time)
                    + "\tCh. "
                    + str(msg.channel)
                    + "\tNote Off\t\t"
                    + get_note_name(msg.note)
                )
            case "control_change":
                if msg.control in cc_to_name:
                    control_type = cc_to_name[msg.control]
                    match control_type:
                        case "Reverb":
                            print(
                                str(time)
                                + "\tCh. "
                                + str(msg.channel)
                                + "\tControl Change\t\t"
                                + str(control_type)
                                + "   \t\t"
                                + str(round(msg.value / 1.27, 2))
                                + "%"
                            )
                        case "Panning":
                            if msg.value < 64:
                                print(
                                    str(time)
                                    + "\tCh. "
                                    + str(msg.channel)
                                    + "\tControl Change\t\tPanning\t\t\t"
                                    + str(round((-msg.value + 64) / 0.64, 2))
                                    + "% Left"
                                )
                            elif msg.value > 64:
                                print(
                                    str(time)
                                    + "\tCh. "
                                    + str(msg.channel)
                                    + "\tControl Change\t\tPanning\t\t\t"
                                    + str(round((msg.value - 64) / 0.63, 2))
                                    + "% Right"
                                )
                            else:
                                print(
                                    str(time)
                                    + "\tCh. "
                                    + str(msg.channel)
                                    + "\tControl Change\t\tPanning\t\t\t0"
                                )
                        case _:
                            print(
                                str(time)
                                + "\tCh. "
                                + str(msg.channel)
                                + "\tControl Change\t\t"
                                + str(control_type)
                                + "   \t\t"
                                + str(msg.value)
                            )
                else:
                    print(
                        str(time)
                        + "\tCh. "
                        + str(msg.channel)
                        + "\tControl Change\t\tCC "
                        + str(msg.control)
                        + " \t\t\t"
                        + str(msg.value)
                    )
            case "program_change":
                if msg.program < 94:
                    print(
                        str(time)
                        + "\tCh. "
                        + str(msg.channel)
                        + "\tProgram Change\t\t"
                        + dk64_instrument_list[msg.program]
                    )
                else:
                    print(
                        str(time)
                        + "\tCh. "
                        + str(msg.channel)
                        + "\tProgram Change\t\tN/A"
                    )
            case "pitchwheel":
                if msg.pitch < 0:
                    print(
                        str(time)
                        + "\tCh. "
                        + str(msg.channel)
                        + "\tControl Change\t\tPitch\t\t       -"
                        + str(round((-msg.pitch) / 4096, 2))
                        + " ST"
                    )
                elif msg.pitch > 0:
                    print(
                        str(time)
                        + "\tCh. "
                        + str(msg.channel)
                        + "\tControl Change\t\tPitch\t\t       +"
                        + str(round((msg.pitch) / 4095.5, 2))
                        + " ST"
                    )
                else:
                    print(
                        str(time)
                        + "\tCh. "
                        + str(msg.channel)
                        + "\tControl Change\t\tPitch\t\t\t0 ST"
                    )
            case "aftertouch":
                print(
                    str(time)
                    + "\tCh. "
                    + str(msg.channel)
                    + "\tControl Change\t\tAftertouch\t\t"
                    + str(msg.value)
                )
            case "track_name":
                print(str(time) + "\tMeta\tTrack Name\t\t" + msg.name)
            case "set_tempo":
                print(
                    str(time)
                    + "\tMeta\tTempo Change\t\t"
                    + str(round(tempo2bpm(msg.tempo), 3))
                )
            case "end_of_track":
                print(str(time) + "\tMeta\tEnd of Track")
            case "sequence_number":
                print(str(time) + "\tMeta\tSequence Number\t\t" + str(msg.number))
            case "time_signature":
                print(
                    str(time)
                    + "\tMeta\tTime Signature\t\t"
                    + str(msg.numerator)
                    + "/"
                    + str(msg.denominator)
                )
            case "key_signature":
                print(str(time) + "\tMeta\tKey Signature\t\t" + str(msg.key))
            case "channel_prefix":
                print(str(time) + "\tMeta\tChannel Prefix")
            case "instrument_name":
                print(str(time) + "\tMeta\tInstrument Name\t\t" + msg.name)
            case "midi_port":
                print(str(time) + "\tMeta\tMidi Port\t\t" + str(msg.port))
            case "marker":
                print(str(time) + '\tMeta\tMarker\t\t\t"' + str(msg.text) + '"')
            case "text":
                print(str(time) + '\tMeta\tText\t\t\t"' + str(msg.text) + '"')
            case "smpte_offset":
                print(
                    str(time)
                    + "\tMeta\tSMPTE Offset\t\t"
                    + str(f"{msg.hours:02d}")
                    + ":"
                    + str(f"{msg.minutes:02d}")
                    + ":"
                    + str(f"{msg.seconds:02d}")
                    + ":"
                    + str(f"{int((msg.frames / msg.frame_rate) * 100):02d}")
                )
            case "sysex":
                print(
                    str(time)
                    + "\tMeta\tSysEx Message\n----------------"
                    + str(msg.data)
                )
            case "copyright":
                print(str(time) + '\tMeta\tCopyright\t\t\t"' + str(msg.text) + '"')
            case _:
                print(
                    str(time) + "\tMeta\tUnknown Message\n----------------" + str(msg)
                )
    print("\n")


def read_midi_data(midi: MidiFile):
    track_number = 0
    for track in midi.tracks:
        print("= Track " + str(track_number + 1) + " =\n")
        read_msg_data(track, track_number)
        track_number += 1


def read_single_track(midi: MidiFile, track_id):
    track_number = track_id - 1
    track = midi.tracks[track_number]
    read_msg_data(track, track_number)


#


def read_midi(midi_file: str):
    midi = MidiFile(midi_file)
    global sharp_or_flat
    sharp_or_flat = "sharp"  # 'sharp' or 'flat'
    read_midi_data(midi)
    # read_single_track(midi, 16)  # Track number 1-16 or 1-18 before FL fixing


read_midi(filedialog.askopenfilename())
