#!/usr/bin/python3

import pickle
import numpy as np
from math import cos, sin, sqrt

# https://pypi.org/project/numpy-stl/
import stl
from stl import mesh

# Performance mesuring
import memory_profiler
import time

# Global variables
from record_globals import precision, tau, rpm, depth, incrNum, amplitude
from record_globals import radius, innerHole, innerRad, outerRad, rH
from record_globals import truncate, _3DShape

# Generate circumference of cylinder
def circumference_generator(t, r, i = truncate(incrNum, precision)):
  while t < tau:
    yield [r * sin(t), r * cos(t)]
    t += i

# Generate perimeter of polygon
def polygon_generator(r, e):
  return circumference_generator(0, r, tau / e)

def expand_points(lst, n) -> list:
  vectors = []
  lst += [lst[0]]
  for i in range(len(lst) - 1):
    a, b = lst[i], lst[i+1]
    vectors += [(b[0] - a[0], b[1] - a[1])]
    i += 1
  
  expanded = []
  for elem, vec in zip(lst, vectors):
    x, y = vec[0] / n, vec[1] / n
    for i in range(n):
      expanded += [(i * x + elem[0], i * y + elem[1])]
  
  return expanded

#Add z position to each vector of x and y
def setzpos(arr, h=0) -> tuple:
  for lst in arr:
      yield(lst[0], lst[1], h)
      
# Combine the vectors in to an outer and inner circle
def calculate_record_shape(recordShape = _3DShape()) -> mesh.Mesh:
  edge_num = 8
  spacingUpper = list(setzpos(circumference_generator(0, innerRad), rH))
  outerGrooveEdgeUpper = list(setzpos(circumference_generator(0, outerRad), rH))

  
  length = len(spacingUpper) // edge_num
  expanded = expand_points(list(polygon_generator(innerHole / 2, edge_num)), length)
  centerHoleUpper = list(setzpos(expanded, rH))
  centerHoleLower = list(setzpos(expanded))
  
  expanded = expand_points(list(polygon_generator(radius, edge_num)), length)
  outerEdgeUpper = list(setzpos(expanded, rH))
  outerEdgeLower = list(setzpos(expanded))

  
  print("Condense vertices into a single list")
  outer = outerEdgeUpper + outerEdgeLower
  outerGroove = outerGrooveEdgeUpper
  center = centerHoleUpper + centerHoleLower
  spacing = spacingUpper
  lst = outer + outerGroove + center + spacing

  print("Add vertices to shape")
  recordShape.add_vertices(lst)

  #Set faces
  print("Constructing faces")
  recordShape.tristrip(outerEdgeUpper, outerGrooveEdgeUpper)
  recordShape.tristrip(centerHoleUpper, spacingUpper)
  
  print("Construct center hole")
  centerHoleUpper = list(setzpos(polygon_generator(innerHole / 2, edge_num), rH))
  centerHoleLower = list(setzpos(polygon_generator(innerHole / 2, edge_num)))
  centerHoleUpper += [centerHoleUpper[0]]
  centerHoleLower += [centerHoleLower[0]]
  recordShape.tristrip(centerHoleUpper, centerHoleLower)
  centerHoleUpper.reverse()
  centerHoleLower.reverse()
  recordShape.tristrip(centerHoleUpper, centerHoleLower)
  
  print("Construct outer perimeter vertical")
  outerEdgeUpper = list(setzpos(polygon_generator(radius, edge_num), rH))
  outerEdgeLower = list(setzpos(polygon_generator(radius, edge_num)))
  outerEdgeUpper += [outerEdgeUpper[0]]
  outerEdgeLower += [outerEdgeLower[0]]
  recordShape.tristrip(outerEdgeUpper, outerEdgeLower)
  outerEdgeUpper.reverse()
  outerEdgeLower.reverse()
  recordShape.tristrip(outerEdgeUpper, outerEdgeLower)

  print("Construct base")
  recordShape.tristrip(outerEdgeLower, centerHoleLower)
  centerHoleLower.reverse()
  outerEdgeLower.reverse()
  recordShape.tristrip(outerEdgeLower, centerHoleLower)
  
  print("Construct top")
  baseline = rH - 0.05
  outerEdgeMiddle = list(setzpos(polygon_generator(radius, edge_num), baseline))
  centerHoleMiddle = list(setzpos(polygon_generator(innerHole / 2, edge_num), baseline))
  outerEdgeMiddle += [outerEdgeMiddle[0]]
  centerHoleMiddle += [centerHoleMiddle[0]]
  recordShape.add_vertices(outerEdgeMiddle + centerHoleMiddle)

  recordShape.tristrip(outerEdgeMiddle, centerHoleMiddle)
  outerEdgeMiddle.reverse()
  centerHoleMiddle.reverse()
  recordShape.tristrip(outerEdgeMiddle, centerHoleMiddle)
  
  return recordShape

def main():
  filename = str(rpm) + '_disc.stl'
  print('Generating blank record.')
  recordShape = calculate_record_shape()
  recordShape.remove_duplicate_faces()
  #Create pickle of recordShape
  print("Pickling record shape.")
  f = open("pickle/{}_shape.p".format(rpm), 'wb')
  pickle.dump(recordShape, f, pickle.HIGHEST_PROTOCOL)

  # Save mesh for debugging purposes
  record_mesh = recordShape.shape_to_mesh()
  print("Saving file to {}".format(filename))
  record_mesh.save("stl/" + filename)
  
  print("Vertices: " + str(len(recordShape.get_vertices())))
  print("Faces: " + str(len(recordShape.get_faces())))
  
  return recordShape

if __name__ == '__main__':
  m1 = memory_profiler.memory_usage()
  t1 = time.process_time()
  main()
  t2 = time.process_time()
  m2 = memory_profiler.memory_usage()
  time_diff = t2 - t1
  mem_diff = m2[0] - m1[0]
  print(f"It took {time_diff:.2f} Secs and {mem_diff:.2f} Mb to execute this method")
