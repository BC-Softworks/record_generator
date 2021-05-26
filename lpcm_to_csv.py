# Used for converting multi and single channel uncompressed
# audio to a single waveform for analog transcription.

import wave # https://docs.python.org/3/library/wave.html
import numpy as np # https://numpy.org/
import math
import sys

# Bit depths of 8, 16, and 32 are supported for conversion
# However, a bit depth of 12 is the max range a standard record player

supported_formats = ['wav', 'wave']

if sys.argv.length != 2 :
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

  
with wave.open(fileName, 'rb') as wav:
  number_of_frames = wav.getnframes()
  numch = wav.getnchannels()
  depth = wav.getsampwidth()
  bit_depth = depth*8;
  auto_data = np.frombuffer(w.readframes(numframes), dtype=np.byte)
  merged = np.zeros((numframes,), dtype=np.byte)
  with open(fileName.split(".")[0] + '.csv', 'w', newline='') as csvfile:
    for i in range(0, numch):
      print ("Extracting {} / {} channels, {} depth".format(i+1, numch, bit_depth))
      ch_data = auto_data[channel::nch]
      merged = np.add(merged, ch_data)
    # Normalized data and append to csv  
    for i in range(0, numch)
      if merged[i] > 2**(bit_depth - 1):
        merged[i] = (merged[i]-2**bit_depth)
      elif merged[i] == 2**(bit_depth - 1):
        merged[i] = 0
      csvfile.append(merged[i] + ',')
