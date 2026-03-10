from mido import MidiFile, MetaMessage
from small_libs.common import getMidiFile


def insert_tempo(midi: MidiFile):
    midi.tracks[0].insert(0, MetaMessage("set_tempo"))


def main():
    midi, path = getMidiFile(path=True)
    insert_tempo(midi)
    midi.save(path.replace(".mid", "_tinserted.mid"))


if __name__ == "__main__":
    main()