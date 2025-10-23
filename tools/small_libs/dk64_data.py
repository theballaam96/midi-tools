"""
Separated out dk64 music related data for quick reference in other files / future files
"""

max_voices = 44
"""max voices dk64 can play at once"""

reverb_tail = 2334000
"""length of reverb tail in microseconds"""


def get_instrument_release(instrument: int):
    """
    returns the release time of an instrument in microseconds
    """
    match instrument:
        # String Sustain
        case 18:
            return 350000
        # Theremin
        case 27:
            return 350000
        # All other instruments
        case _:
            return 0


def get_pitch_range(instrument: int):
    """
    returns pitch bend range in ±Semitones based on instrument patch/instrument number
    """

    match instrument:
        # Trombone
        case 16:
            return 5
        # Theremin
        case 27:
            return 12
        # Timpani
        case 29:
            return 5
        # Wind SFX
        case 41:
            return 12
        # Owl & Wolf SFX
        case 75:
            return 8
        # Electric Guitar (Ext. PBend)
        case 76:
            return 5
        # All other instruments
        case _:
            return 2


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
    "Aztec Bell",
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
"""
The DK64 Standardized Instrument list v6.1
"""
