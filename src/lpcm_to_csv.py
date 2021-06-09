#!/usr/bin/env python

# Runs on Python 3.8 and above
# Used for converting multi and single channel uncompressed
# audio to a single waveform for analog transcription.

import aifc # https://docs.python.org/3/library/aifc.html#module-aifc
import wave # https://docs.python.org/3/library/wave.html
import numpy as np # https://numpy.org/
import math
import sys

# Bit depths of 8, 16, and 32 are supported for conversion
# However, a bit depth of 12 is the max range of a standard record player

from enum import Enum

# Create Enum for mono and stereo
class audio_mode(Enum):
  MONO = 1
  STEREO = 2

# Averages the wave for each channel
def process_channels(auto_data, numch, numframes):
  merged = np.zeros((numframes//numch,), dtype=np.byte)
  for i in range(0, numch):
    print ("Extracting {} / {} channels, {} depth".format(i+1, numch, bit_depth))
    ch_data = auto_data[i:numframes:numch]
    print(len(ch_data))
    merged = np.add(merged, ch_data)
  return np.divide(merged, numch)

def normalize_data(arr, numch, depth):
  assert depth > 0
  bit_depth = depth*8
  for i in range(0, numch):
    if arr[i] > 2**(bit_depth - 1):
      arr[i] = (arr[i]-2**bit_depth)
    elif arr[i] == 2**(bit_depth - 1):
      arr[i] = 0
  return arr

def write_channels(merged, filename):
  csvfile = open(filename.split(".")[0] + '.csv', 'w', newline='')
  for item in merged.astype(str):
    csvfile.write(item + ',')
  # Write a zero at the end of the file to supress the extra ','
  csvfile.write('0')
  csvfile.close()

def aifctocsv(filename, mode=audioMode.MONO):
  with aifc.open(filename, 'rb') as aif:
    numframes = aif.getnframes()
    numframes -= numframes % 2

    numch = aif.getnchannels()
    depth = aif.getsampwidth()
    # Create buffer for audio channel(s)
    auto_data = np.frombuffer(aifc.readframes(numframes), dtype=np.byte)
    merged = process_channels(auto_data, numch, numframes)
    write_channels(normalize_data(merged, numch, depth), filename)

def wavetocsv(filename, mode=audioMode.MONO):
  with wave.open(filename, 'rb') as wav:
    numframes = wav.getnframes()
    numframes -= numframes % 2
    
    numch = wav.getnchannels()
    depth = wav.getsampwidth()
    auto_data = np.frombuffer(wav.readframes(numframes), dtype=np.byte)

    # Averages the wave for each channel
    merged = process_channels(auto_data, numch, numframes)
    write_channels(normalize_data(merged, numch, depth), filename)

def main():
  if len(sys.argv) != 2 :
    print('Wrong number of arguements.')
    quit()

  filename = sys.argv[1]
  if '.' not in filename:
    print('File extension must be provided.')
    quit()

  extension = filename.split(".")[1]

    
  if extension in ['wav', 'wave']:
    wavetocsv(filename)
  elif extension in ['aifc', 'aiff']:
    aifctocsv(filename)
  else:
    print('Not a supported file format.')
    quit()

#Run program
if __name__ == '__main__':
  main()
