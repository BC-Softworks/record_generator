# Used for converting multi and single channel uncompressed
# audio to a single waveform for analog transcription.

import aifc # https://docs.python.org/3/library/aifc.html
import wave # https://docs.python.org/3/library/wave.html
import csv  # https://docs.python.org/3/library/csv.html
import numpy as np # https://numpy.org/
import math
import sys

# Variables for unpacking
import record_constant.samplingRate
bitdepth = 8
# Bit depths of 8, 12, 16, and 24 are supported for conversion
# However, a bit depth of 12 is the max range a standard record player

supported_formats = ['wav', 'wave', 'aifc', 'aiff']

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

def getbytesarray(λ):
  with λ.open(fileName, 'rb') as file:
    number_of_frames = λ.getnframes()
    return np.frombuffer(file.readframes(numframes), np.byte)
  
if extension in ['wav', 'wave']:
  getbytesarray(wave)
else:
  getbytesarray(afic)

with open(fileName.split(".")[0] + '.csv', 'w', newline='') as csvfile:
      csv_writer = csv.writer(csvfile, delimiter=' ')  
      
          
