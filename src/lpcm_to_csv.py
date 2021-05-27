#!/usr/bin/env python

# Runs on Python 3.8 and above
# Used for converting multi and single channel uncompressed
# audio to a single waveform for analog transcription.

import wave # https://docs.python.org/3/library/wave.html
import numpy as np # https://numpy.org/
import math
import sys

# Bit depths of 8, 16, and 32 are supported for conversion
# However, a bit depth of 12 is the max range of a standard record player

supported_formats = ['wav', 'wave']
create_single_channel_copy = true

def wavetocsv():
  with wave.open(filename, 'rb') as wav:
    numframes = wav.getnframes()
    if numframes % 2 == 1:
      numframes -= 1
    numch = wav.getnchannels()
    depth = wav.getsampwidth()
    bit_depth = depth*8;
    auto_data = np.frombuffer(wav.readframes(numframes), dtype=np.byte)
    merged = np.zeros((numframes//numch,), dtype=np.byte)

    csvfile = open(filename.split(".")[0] + '.csv', 'w', newline='')
    
    # Averages the wave for each channel
    for i in range(0, numch):
      print ("Extracting {} / {} channels, {} depth".format(i+1, numch, bit_depth))
      ch_data = auto_data[i:numframes:numch]
      print(len(ch_data))
      merged = np.add(merged, ch_data)
    merged = np.divide(merged, numch)
    
    # Normalize data and append to csv  
    for i in range(0, numch):
      if merged[i] > 2**(bit_depth - 1):
        merged[i] = (merged[i]-2**bit_depth)
      elif merged[i] == 2**(bit_depth - 1):
        merged[i] = 0
    for item in merged.astype(str):
      csvfile.write(item + ',')
    csvfile.close()
    return (merged, depth)

def main():
  if len(sys.argv) != 2 :
    print('Wrong number of arguements.')
    quit()
  
  filename = sys.argv[1]
  if '.' not in filename:
    print('File extension must be provided.')
    quit()    
  
  extension = filename.split(".")[1]
  if extension not in supported_formats:
    print('Not a supported file format.')
    quit()
  
  wavetocsv(filename)
  
main()  
