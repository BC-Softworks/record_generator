import wave # https://docs.python.org/3/library/wave.html
import csv # https://docs.python.org/3/library/csv.html
import math
import sys

# Variables for unpacking
import record_constant.samplingRate


if sys.argv.length != 2 :
  print('Wrong number of arguements.')
  quit()

if sys.argv[1].endswith('.wav') :
  print('Not a wave file.')
  quit()  

filename = sys.argv[1]

with wave.open(fileName, 'rb') as w_file:
  channels = wave.getnchannels()
  number_of_frames = wave.getnframes()
  with open(fileName[:-4] + '.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=' ')
    
