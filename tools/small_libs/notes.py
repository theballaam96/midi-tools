"""
Note name functions for quick reference in other files / future files and to condense code a little
Reminder: use set_sharp_or_flat(...) before get_note_name(...), or don't :3
"""

note_names = ["Do", "Di", "Re", "Ri", "Mi", "Fa", "Fi", "Sol", "Si", "La", "Li", "Ti"]


def set_sharp_or_flat(sign: str):
    """
    Sets the sign for the notes to 'sharp' or 'flat'
    """

    global note_names
    if sign == "flat":
        note_names = [
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
    else:
        note_names = [
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


def get_note_name(note: int):
    """
    Retrieves the note name from the Midi note number.
    """

    note_name = f"{ note_names[note % 12] }{ int(note / 12) }"
    return note_name
