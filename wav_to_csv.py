import wave
import csv
import math
import sys

if sys.argv.length != 2 :
  print('Wrong number of arguements.')
  quit()

if sys.argv[1].endswith('.wav') :
  print('Not a wave file.')
  quit()  

filename = sys.argv[1]

with wave.open(fileName, 'rb') as w_file:
  with open(fileName[:-4] + '.csv', 'w', newline='') as csvfile:
    
