#!/usr/bin/python3

import numpy as np
import os
from math import cos, sin, sqrt, pow

# https://pypi.org/project/numpy-stl/
import stl
from stl import mesh

# Performance mesuring
import memory_profiler
import time

# Global variables
import record_globals as rg
from record_globals import *

# Generate circumference of cylinder
def circumference_generator(t, r, i = incrNum):
  while t < tau:
    yield r * sin(t), r * cos(t)
    t += i

# Generate perimeter of polygon
def polygon_generator(r, e):
  return circumference_generator(0, r, tau / e)

#Add z position to each vector of x and y
def setzpos(arr, h=0) -> tuple:
  for lst in arr:
      yield(lst[0], lst[1], h)
      
def create_polygon(r, n, h=0):
  lst = list(polygon_generator(r, n))
  return list(setzpos(lst, h))
  
def add_polygon_edges(a, b, shape):
  a.append(a[0])
  b.append(b[0])
  shape.tristrip(a, b)
  return shape
  
# Combine the vectors in to an outer and inner circle
def calculate_record_shape(recordShape = rg._3DShape(), info = True) -> mesh.Mesh:
  edge_num = 8
  baseline = rH - 0.05
    
  outerEdgeUpper = create_polygon(radius, edge_num, rH)
  outerEdgeLower = create_polygon(radius, edge_num)

  outerLipRad = outerRad + 7
  outerSpacerUpper = create_polygon(outerLipRad, edge_num, rH)
  outerSpacerMiddle = create_polygon(outerLipRad, edge_num, baseline)
  outerSpacerLower = create_polygon(outerLipRad, edge_num, baseline)


  innerSpacerUpper = create_polygon(innerRad, edge_num, rH)
  innerSpacerMiddle = create_polygon(innerRad, edge_num, baseline)

  center_radius = innerHole / 2
  centerHoleUpper = create_polygon(center_radius, edge_num, rH)
  centerHoleLower = create_polygon(center_radius, edge_num)

  if (info):
    print("Adding vertices to the shape")
    
  recordShape.add_vertices(outerEdgeUpper + outerEdgeLower)
  recordShape.add_vertices(outerSpacerUpper + outerSpacerMiddle + outerSpacerLower)
  recordShape.add_vertices(innerSpacerUpper + innerSpacerMiddle)
  recordShape.add_vertices(centerHoleUpper + centerHoleLower)
  if (info):
    vertices = recordShape.get_vertices()
    print("Number of vertices: " + str(len(vertices)))
  
  if (info):
    print("Create faces:\n  Draw vertical faces")
  
  recordShape = add_polygon_edges(outerEdgeUpper, outerEdgeLower, recordShape)
  recordShape = add_polygon_edges(outerSpacerUpper, outerSpacerMiddle, recordShape)
  recordShape = add_polygon_edges(outerSpacerMiddle, outerSpacerLower, recordShape)
  recordShape = add_polygon_edges(innerSpacerUpper, innerSpacerMiddle, recordShape)
  recordShape = add_polygon_edges(centerHoleUpper, centerHoleLower, recordShape)
  
  if (info):
    print("  Draw horizontial faces")

  recordShape = add_polygon_edges(outerEdgeUpper, outerSpacerUpper, recordShape)
  recordShape = add_polygon_edges(innerSpacerUpper, centerHoleUpper, recordShape)
  recordShape = add_polygon_edges(outerSpacerMiddle, innerSpacerMiddle, recordShape)
  recordShape = add_polygon_edges(outerEdgeLower, centerHoleLower, recordShape)

  if (info):
    print("Number of faces: " + str(len(recordShape.get_faces())))
  return recordShape

def main():
  filename = str(rpm) + '_disc.stl'
  print('Generating blank record.')
  recordShape = calculate_record_shape()
  recordShape.remove_duplicate_faces()
  recordShape.remove_empty_faces()
  

  # Save mesh for debugging purposes
  if(not os.path.isdir('stl')):
      os.mkdir('stl')
  record_mesh = recordShape.shape_to_mesh()
  print("Saving file to {}".format(filename))
  record_mesh.save("stl/" + filename)
  
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
