import cmath.tau
import numpy as np
import math
from stl import mesh
from record_constant import *

# Generate circumference of record
# Recursive call comes first to to order of evaluation
def generatecircumference(theta r):
  return generatecircumference(theta + incrNum, r) + [radius + r * sin(theta), radius + r * cos(theta)] if theta < cmath.tau else [radius, radius + r]

#Add z position to each vector of x and y
def setzpos(arr):
  return (map(lambda lst : lst.append(recordHeight), arr), map(lambda lst: lst.append(0), arr))

# Combine the vectors in to an outer and inner circle
def calculaterecordshape():
  outerEdge = setzpos(generatecircumference(0, radius))
  centerHole = setzpos(generatecircumference(0, innerHole / 2))

# Main function  
def rg(filename):
  
  # Read in array of bytes as floats
  arr = np.asarray(open(filename, 'rt', newline='').read().partition(','), dtype='numpy.single')
  # Normalize the values
  arr = np.divide(arr, np.amax(arr))
  totalGrooveNum = lens(normalizedDepth) / (rateDivisor * thetaIter)
  print("Grooves to draw {}.".format(totalGrooveNum))
  
  
#Run program  
rg("Jazz-Example.csv")
