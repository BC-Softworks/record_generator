#!/usr/bin/env python

import stl
from stl import mesh

import pickle
import numpy as np
from math import cos, sin

from matplotlib import pyplot
from mpl_toolkits import mplot3d

from record_globals import precision, tau, rpm, depth, incrNum
from record_globals import radius, innerHole, innerRad, rH
from record_globals import truncate, _3DShape

# Generate circumference of record
# Recursive call comes first to to order of evaluation
def generatecircumference(t, r) -> list:
  lst = []
  while t < tau:
    lst.append([r * sin(t), r * cos(t)])
    t += truncate(incrNum, precision)

  return lst

#Add z position to each vector of x and y
def setzpos(arr) -> tuple:
  x = list()
  y = list()
  for lst in arr:
      x = x + [(lst[0], lst[1], rH)]
      y = y + [(lst[0], lst[1], 0.0)]
  
  assert len(x[0]) == 3
  return (x , y)

# Combine the vectors in to an outer and inner circle
def calculate_record_shape(recordShape = _3DShape()) -> mesh.Mesh:

  (outerEdgeUpper, outerEdgeLower) = setzpos(generatecircumference(0, radius))
  (centerHoleUpper, centerHoleLower) = setzpos(generatecircumference(0, innerHole / 2))
  (spacingUpper, spacingLower) = setzpos(generatecircumference(0, innerRad))
  
  print("Condense vertices into a single list")
  outer = outerEdgeUpper + outerEdgeLower
  center = centerHoleUpper + centerHoleLower
  spacing = spacingUpper + spacingLower
  lst = outer + center + spacing

  print("Add vertices to shape")
  recordShape.add_vertices(lst)

  #Set faces
  print("Connecting vertices")
  recordShape.tristrip(spacingLower, outerEdgeLower)
  recordShape.tristrip(outerEdgeLower, outerEdgeUpper)
  
  recordShape.tristrip(centerHoleUpper, spacingUpper)
  recordShape.tristrip(centerHoleLower, spacingLower)
  recordShape.tristrip(spacingLower, spacingUpper)
  recordShape.tristrip(centerHoleUpper, centerHoleLower)

  return recordShape

def shape_to_mesh(shape) -> mesh.Mesh:
  faces = shape.get_faces()
  vertices = shape.get_vertices()
  rec = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
  for i, f in enumerate(faces):
    for j in range(3):
      rec.vectors[i][j] = vertices[f[j],:]
  return rec

def main():
  filename = str(rpm) + '_disc.stl'
  print('Generating blank record.')
  recordShape = calculate_record_shape()

  #Create pickle of recordShape
  print("Pickling record shape.")
  f = open("pickle/{}_shape.p".format(rpm), 'wb')
  pickle.dump(recordShape, f, pickle.HIGHEST_PROTOCOL)

  # Save mesh for debugging purposes
  record_mesh = shape_to_mesh(recordShape)
  print("Saving file to {}".format(filename))
  record_mesh.save("stl/" + filename)

if __name__ == '__main__':
  main()
