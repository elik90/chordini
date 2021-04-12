from pathlib import Path
import os
import music21 as m21
import numpy as np
import pandas as pd
import json
import xml.etree.ElementTree as ET
from itertools import groupby

root_path = Path.cwd()
full_path = Path.joinpath(root_path, "MXLs/")
MXL_DATA_PATH = "Users\ikhwan\PycharmProjects\pythonProject\chordini\MXLs"
NUM_CHORDS = "num_chords.txt"
# 16th, eighth, dotted-eighth, quarter, dotted-quarter, half, dotted-half, whole
ACCEPTABLE_DURATIONS = [
    0.25,
    0.5,
    0.75,
    1.0,
    1.5,
    2,
    3,
    4,
]


# load song data
def load_mxls(mxl_path):
    song_titles = []
    songs = []

    # search all sub folders
    for path, sub_dirs, files in os.walk(mxl_path):
        print(f"path {path}")
        for file in files:
            if file[-3:] == "mxl":
                try:
                    song_path = os.path.join(path, file)
                    song = m21.converter.parseFile(song_path)
                    # drop suffix
                    file_short = file[:-4]
                    song_titles.append(file_short)
                    songs.append(song)
                except (ZeroDivisionError, ET.ParseError):
                    # deleting corrupted song data
                    os.remove(song_path)
                    pass
    return songs, song_titles

# transpose key of song to Cmaj
def transpose(song):
    # get key from song from .mxl file
    p = m21.analysis.discrete.KrumhanslSchmuckler()
    song_key = p.getSolution(song)

    # estimate key using music21
    if not isinstance(song_key, m21.key.Key):
        song_key = song.analyze("key")

    # get interval for transposition
    if song_key.mode == "major":
        interval = m21.interval.Interval(song_key.tonic, m21.pitch.Pitch("C"))
    elif song_key.mode == "minor":
        interval = m21.interval.Interval(song_key.tonic, m21.pitch.Pitch("A"))
    else:
        interval = None

    # transpose song by calculated interval using m21.transpose
    transposed_song = song.transpose(interval)

    return transposed_song


# extracting chord from song for progression data
def encode_song(song):
    encoded_song = []

    for event in song.flat.notesAndRests:
        # handle chords
        if isinstance(event, m21.chord.Chord):

            try:
                c_symbol = str(event.figure)
                c_symbol = c_symbol.replace(" ", "")
                encoded_song.append(c_symbol)
            except AttributeError:
                pass

    # removing consecutive duplicates
    encoded_song = [x[0] for x in groupby(encoded_song)]

    # cast encoded song to a string
    encoded_song = " ".join(map(str,encoded_song))
    return encoded_song


# extracting chord information for each chord
def build_chord_roman_dicts(song):
    song_chord_dict ={}
    song_roman_dict = {}
    for event in song.flat.notesAndRests:
        # handle chords
        if isinstance(event, m21.chord.Chord):

            try:
                # capture pitches
                notes = [str(p) for p in event.pitches]
                song_chord_dict[str(event.figure).replace(" ", "")] = notes
                # capture roman numeral
                event.key = m21.key.Key('C')
                song_roman_dict[str(event.figure)] = event.romanNumeral.figure
            except AttributeError:
                pass
    return song_chord_dict, song_roman_dict

# create pandas dataframe and master dictionaries to append with data from each song
def preprocess(songs, song_titles):
    songs_df = pd.DataFrame(columns=['song_title', 'chord_progression'])
    chord_dict = {}
    roman_dict = {}
    # analyze each song
    print(f"total {len(songs)} songs")
    for i, song in enumerate(songs):
        # progress indicator
        print(i, end="\r")
        # transpose song to Cmaj/Amin
        song = transpose(song)

        # encode songs
        encoded_song = encode_song(song)
        # build song dicts
        song_chord_dict, song_roman_dict = build_chord_roman_dicts(song)

        # append song dict values to master
        for chord in song_chord_dict:
            chord_dict[chord] = song_chord_dict[chord]
        for chord in song_roman_dict:
            roman_dict[chord] = song_roman_dict[chord]

        # save data to dataframe
        song_data = {'song_title': song_titles[i], 'chord_progression': encoded_song}
        song_ser = pd.Series(data=song_data)
        songs_df = songs_df.append(song_ser, ignore_index=True)

    songs_df['chord_list'] = songs_df['chord_progression'].apply(lambda x: list(x.split(' ')))
    songs_df['num_unique'] = songs_df['chord_list'].apply(lambda x: len(set(x)))
    return songs_df, chord_dict, roman_dict


# write dataframe to csv for notebook import
def df_to_csv(dataframe, df_name):
    dataframe.to_csv(df_name, index=False, mode='w+')
    print(f"{df_name}.csv has been created.")


# write dictionaries to json for notebook import
def dict_to_json(my_dict, filename):
    with open(filename, 'w') as f:
        json.dump(my_dict, f, indent=4)


# load file (generic)
def load(file_path):
    with open(file_path, "r") as fp:
        song = fp.read()
    return song


def main():
    # load songs
    print("loading songs...")
    songs, titles = load_mxls(full_path)
    print(f"Loaded {len(songs)} songs.")

    # extract chords: create dataset and songs_df.csv
    songs_df, chord_dict, roman_dict = preprocess(songs, titles)
    print("preprocessing done...")
    df_to_csv(songs_df, 'songs_df.csv')

    print(songs_df)

    dict_to_json(chord_dict, 'chord_dict.json')
    dict_to_json(roman_dict, 'roman_dict.json')


if __name__ == "__main__":
    main()

