from cmath import tau
import numpy as np
import math
from stl import mesh
from record_constant import *

# Generate circumference of record
# Recursive call comes first to to order of evaluation
def generatecircumference(theta, r):
  return generatecircumference(theta + incrNum, r) + [radius + r * sin(theta), radius + r * cos(theta)] if theta < tau else [radius, radius + r]

#Add z position to each vector of x and y
def setzpos(arr):
  return (np.asarray(map(lambda lst : lst.append(recordHeight), arr)), np.asarray(map(lambda lst: lst.append(0), arr)))

# Combine the vectors in to an outer and inner circle
def calculaterecordshape():
  outerEdge = setzpos(generatecircumference(0, radius))
  centerHole = setzpos(generatecircumference(0, innerHole / 2))

#Outer Upper vertex
def ou(r, a, b, theta):
  w = r + a * b
  return (r + w * cos(theta), r + w * sin(theta))

#Inner Upper vertex
def iu(r, a, b, theta):
  w = r - gW - a * b
  return (r + w * cos(theta), r + w * sin(theta))

#Outer Lower vertex
def ol(r, a, theta):
  return ( r + r * cos(theta), r + r * sin(theta))

#Inner Lower vertex
def il(r, a, theta):
  w = r - gW
  return ( r + w * cos(theta), r + w * sin(theta))

def grooveHeight(audio_array):
  return recordHeight-depth-amplitude+audio_array[rateDivisor*samplenum];

# r is the radial postion of the vertex beign drawn
def draw_grooves(audio_array, r):
  #ti is thetaIter
  baseCase = lambda ti : rateDivisor*samplenum < (lens(audio_array)-rateDivisor*ti+1)
               and r > innerRad
  
  if baseCase(thetaIter):
    for theta in range(0, incrNum, tau):
      samplenum += 1
      gH = grooveHeight(audio_array)      
      grooveOuterUpper.append(ou(r, a, b, theta))
      grooveOuterLower.append(iu(r, a, b, theta))
      grooveInnerUpper.append(ol(r, a, theta))
      grooveInnerLower.append(il(r, a, theta))
      r -= radIncr
    
    draw_grooves(audio_array, r)
  # Draw groove cap
  else:
    

# Main function  
def rg(filename):
  
  # Read in array of bytes as floats
  arr = np.asarray(open(filename, 'rt', newline='').read().partition(','), dtype='numpy.single')
  # Normalize the values
  arr = np.divide(arr, np.amax(arr))
  totalGrooveNum = lens(normalizedDepth) // (rateDivisor * thetaIter)
  print("Grooves to draw {}.".format(totalGrooveNum))
  
  draw_grooves(normalizedDepth)

#Run program  
rg("Jazz-Example.csv")
