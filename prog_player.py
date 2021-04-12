import music21 as m21
import json
import sys
OUTPUT_FILE_PATH = 'output_prog'
CHORD_DICT_FILE = 'chord_dict.json'


# load files (generic)
def load_file(file_path):
    with open(file_path, "r") as fp:
        song = fp.read()
    return song


# load dictionaries to map chord definitions
def load_json(file_path):
    with open(file_path, "r") as fp:
        return json.load(fp)


# convert chords for music21 processing
def convert_chords_to_list(output_prog):
    output_list = list(output_prog.split(' '))
    return output_list


# map chords to their pitch contents to create chords for musescore
def convert_chords_to_pitches(progression):
    chord_dict = load_json(CHORD_DICT_FILE)
    output_chord_pitches = [chord_dict[chord] for chord in progression]
    return output_chord_pitches


# creating music21 streams that will be represented in musescore
def create_stream_of_chords(chord_pitches):
    # initialize stream
    output_stream = m21.stream.Stream()
    # set clef to treble
    c = m21.clef.TrebleClef()
    output_stream.append(c)
    # set key to Cmaj
    output_stream.append(m21.key.Key('C'))
    # setting note duration to quarter note
    d = m21.duration.Duration()
    d.quarterLength = 2

    for chord in chord_pitches:
        # defining chord based on pitches
        input_chord = m21.chord.Chord(chord)
        # set chord duration
        input_chord.duration = d
        # add chord to stream
        output_stream.append(input_chord)

    return output_stream


def main():
    # Import output_prog file and chord_dict dictionary
    OUTPUT_FILE_PATH = sys.argv[1]
    output_prog = load_file(OUTPUT_FILE_PATH)
    print(f"output_prog: {output_prog}")

    # convert output_prog into list of chord names
    output_chord_list = convert_chords_to_list(output_prog)
    print(f"output_chord_list: {output_chord_list}")

    # convert output_prog into list of chord pitches
    output_chord_pitches = convert_chords_to_pitches(output_chord_list)
    print(output_chord_pitches)

    # create stream of chords for music21
    output_stream = create_stream_of_chords(output_chord_pitches)

    # play stream of chords via musescore
    output_stream.show()

if __name__ == "__main__":
    main()