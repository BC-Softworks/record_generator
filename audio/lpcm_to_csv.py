#!/usr/bin/env python

"""
  Runs on Python 3.8 and above
  Used for converting multi and single channel uncompressed
  audio to a single waveform for analog transcription.
  Note:
    Bit depths of 8, 16, and 32 are supported for conversion
    However, a bit depth of 12 is the max range of a standard record player
"""

import aifc  # https://docs.python.org/3/library/aifc.html#module-aifc
import sys
import wave  # https://docs.python.org/3/library/wave.html
from enum import Enum
import numpy as np  # https://numpy.org/


class AudioMode(Enum):
    """ Mono or stereo channel sound """
    MONO = 1
    STEREO = 2


def process_channels(auto_data, numch, numframes):
    """ Averages the wave for each channel """
    merged = np.zeros((numframes // numch,), dtype=np.byte)
    for i in range(0, numch):
        print("Extracting {} / {} channels".format(i + 1, numch))
        ch_data = auto_data[i:numframes:numch]
        print(len(ch_data))
        merged = np.add(merged, ch_data)
    return np.divide(merged, numch)


def normalize_data(arr, numch, depth):
    assert depth > 0
    bit_depth = depth * 8
    for i in range(0, numch):
        if arr[i] > 2**(bit_depth - 1):
            arr[i] = (arr[i] - 2**bit_depth)
        elif arr[i] == 2**(bit_depth - 1):
            arr[i] = 0
    return arr


def write_channels(merged, filename):
    """ Write channels to csv file """
    csvfile = open(filename.split(".")[0] + '.csv', 'w', newline='')
    for item in merged.astype(str):
        csvfile.write(item + ',')
    # Write a zero at the end of the file to supress the extra ','
    csvfile.write('0')
    csvfile.close()


def aifctocsv(filename, mode=AudioMode.MONO):
    with aifc.open(filename, 'rb') as aif:
        numframes = aif.getnframes()
        numframes -= numframes % 2

        # Create buffer for audio channel(s)
        auto_data = np.frombuffer(aif.readframes(numframes), dtype=np.byte)
        numch = aif.getnchannels()
        depth = aif.getsampwidth()
        merged = process_channels(auto_data, numch, numframes)
        write_channels(normalize_data(merged, numch, depth), filename)


def wavetocsv(filename, mode=AudioMode.MONO):
    with wave.open(filename, 'rb') as wav:
        numframes = wav.getnframes()
        numframes -= numframes % 2

        auto_data = np.frombuffer(wav.readframes(numframes), dtype=np.byte)

        # Averages the wave for each channel
        numch = wav.getnchannels()
        depth = wav.getsampwidth()
        merged = process_channels(auto_data, numch, numframes)
        write_channels(normalize_data(merged, numch, depth), filename)


def main():
    if len(sys.argv) != 2:
        print('Wrong number of arguements.')
        sys.exit()

    filename = sys.argv[1]
    if '.' not in filename:
        print('File extension must be provided.')
        sys.exit()

    extension = filename.split(".")[1]

    if extension in ['wav', 'wave']:
        wavetocsv(filename)
    elif extension in ['aifc', 'aiff']:
        aifctocsv(filename)
    else:
        print('Not a supported file format.')
        sys.exit()


# Run program
if __name__ == '__main__':
    main()
