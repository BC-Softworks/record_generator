#!/usr/bin/python3

import pickle
import numpy as np
from math import cos, sin

# https://pypi.org/project/numpy-stl/
import stl
from stl import mesh

# Performance mesuring
import memory_profiler
import time

# Global variables
from record_globals import precision, tau, rpm, depth, incrNum
from record_globals import radius, innerHole, innerRad, outerRad, rH
from record_globals import truncate, _3DShape

# Generate circumference of record
def circumference_generator(t, r, i = truncate(incrNum, precision)):
  while t < tau:
    yield [r * sin(t), r * cos(t)]
    t += i
  
#Add z position to each vector of x and y
def setzpos(arr) -> tuple:
  x = list()
  y = list()
  for lst in arr:
      x += [(lst[0], lst[1], rH)]
      y += [(lst[0], lst[1], 0.0)]
  
  assert len(x[0]) == 3
  return (x , y)

# Combine the vectors in to an outer and inner circle
def calculate_record_shape(recordShape = _3DShape()) -> mesh.Mesh:

  (outerEdgeUpper, outerEdgeLower) = setzpos(circumference_generator(0, radius))
  (outerGrooveEdgeUpper, outerGrooveEdgeLower) = setzpos(circumference_generator(0, outerRad))
  (spacingUpper, spacingLower) = setzpos(circumference_generator(0, innerRad))
  (centerHoleUpper, centerHoleLower) = setzpos(circumference_generator(0, innerHole / 2))

  
  print("Condense vertices into a single list")
  outer = outerEdgeUpper + outerEdgeLower
  outerGroove = outerGrooveEdgeUpper + outerGrooveEdgeLower
  center = centerHoleUpper + centerHoleLower
  spacing = spacingUpper + spacingLower
  lst = outer + outerGroove + center + spacing

  print("Add vertices to shape")
  recordShape.add_vertices(lst)

  #Set faces
  print("Construct outer spacer")
  recordShape.tristrip(outerEdgeLower, outerEdgeUpper)
  recordShape.tristrip(outerEdgeLower, outerGrooveEdgeLower)
  recordShape.tristrip(outerEdgeUpper, outerGrooveEdgeUpper)
  recordShape.tristrip(outerGrooveEdgeLower, outerGrooveEdgeUpper)

  print("Construct inner spacer")
  recordShape.tristrip(spacingLower, outerGrooveEdgeLower)  
  recordShape.tristrip(centerHoleUpper, spacingUpper)
  recordShape.tristrip(centerHoleLower, spacingLower)
  
  print("Construct center hole")
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
  m1 = memory_profiler.memory_usage()
  t1 = time.process_time()
  main()
  t2 = time.process_time()
  m2 = memory_profiler.memory_usage()
  time_diff = t2 - t1
  mem_diff = m2[0] - m1[0]
  print(f"It took {time_diff:.2f} Secs and {mem_diff:.2f} Mb to execute this method")
