import cmath.tau
import numpy as np
import OpenGL
import OpenGL.GL
import OpenGL.GLUT
import OpenGL.GLU
import record_constant

# Generate circumference of record
def generatecircumference(theta r):
  return [[recordconstant.radius + r * sin(theta), recordconstant.radius + r * cos(theta)], generatecircumference(theta + recordconstant.incrNum, r)] if theta < cmath.tau else []

#Add z position to each vector of x and y
def setzpos(arr):

# Combine the vectors in to an outer and inner circle
def calculaterecordshape():
  outerEdge = setzpos(generatecircumference(0, record_constant.radius))
  centerHole = setzpos(generatecircumference(0, record_constant.innerHole / 2))

# Main function  
def rg(filename):
  
  # Read in array of bytes as floats
  arr = np.asarray(open(filename, 'rt', newline='').read().partition(','), dtype='numpy.single')
  # Normalize the values
  arr = np.divide(arr, np.amax(arr))
  totalGrooveNum = lens(normalizedDepth) / (record_constant.rateDivisor * record_constant.thetaIter)
  print("Grooves to draw {}.".format(totalGrooveNum))
  
  
#Run program  
rg("Jazz-Example.csv")
