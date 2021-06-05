#!/usr/bin/python3

import stl
from stl import mesh

import pickle
import numpy as np
import math

from matplotlib import pyplot
from mpl_toolkits import mplot3d

import record_constant
from record_constant import *

# Generate circumference of record
# Recursive call comes first to to order of evaluation
def generatecircumference(t, r) -> list:
  lst = []
  while t < record_constant.tau:
    lst.append([radius + r * math.sin(t), radius + r * math.cos(t)])
    # Increasing incrNum for circumference to speed up processing
    # and shave off vertices unnecessary vertices
    # Consider creating seperate constant in record_constant for this function
    t += truncate(incrNum * 25.5, precision)

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
def calculate_record_shape() -> mesh.Mesh:
  recordShape = record_constant._3DShape()
  #Create vector lists
  (outerEdgeUpper, outerEdgeLower) = setzpos(generatecircumference(0, radius))
  (centerHoleUpper, centerHoleLower) = setzpos(generatecircumference(0, innerHole / 2))
  
  print("Condense vertices into a single list")
  outer = outerEdgeUpper + outerEdgeLower
  center = centerHoleUpper + centerHoleLower
  lst = outer + center

  print("Add vertices to shape")
  for vertex in lst:
      recordShape.add_vertex(vertex)

  #Set faces
  print("Connecting vertices")
  recordShape.tristrip(centerHoleUpper, centerHoleLower)
  recordShape.tristrip(centerHoleLower, outerEdgeLower)
  recordShape.tristrip(outerEdgeLower, outerEdgeUpper)
  
  return recordShape

def shape_to_mesh(shape) -> mesh.Mesh:
  faces = shape.get_faces()
  vertices = shape.get_vertices()
  rec = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
  for i, f in enumerate(faces):
    for j in range(3):
      rec.vectors[i][j] = vertices[f[j],:]
  return rec

def display_stl(record_mesh):
  # Create a new plot
  axes = mplot3d.Axes3D(pyplot.figure()) 
  axes.add_collection3d(mplot3d.art3d.Poly3DCollection(record_mesh.vectors))

  # Show the plot to the screen
  pyplot.show()

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
  record_mesh.save("../stl/" + filename)

if __name__ == '__main__':
  main()
