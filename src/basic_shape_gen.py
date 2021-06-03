#!/usr/bin/python3

import stl
from stl import mesh

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
    t += incrNum

  return lst + [[radius, radius + r]]

#Add z position to each vector of x and y
def setzpos(arr):
  x = [lst.append(record_constant.rH) for lst in arr]
  y = [lst.append(0.0) for lst in arr]
  return x, y

# Combine the vectors in to an outer and inner circle
def calculaterecordshape() -> mesh.Mesh:
  recordShape = record_constant._3DShape()
  #Create vector lists
  outerEdgeUpper, outerEdgeLower = setzpos(generatecircumference(0, radius))
  centerHoleUpper, centerHoleLower = setzpos(generatecircumference(0, innerHole / 2))

  for v in outerEdgeUpper + outerEdgeLower + centerHoleUpper + centerHoleLower:
      if v is not None:
          recordShape.add_vertex(v)

  #Set faces
  recordShape.tristrip(centerHoleUpper, centerHoleLower)
  recordShape.tristrip(centerHoleLower, outerEdgeLower)
  recordShape.tristrip(outerEdgeLower, outerEdgeUpper)
  

  faces = record.get_faces()
  vertices = record.get_vertices()
  rec = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
  for i, f in enumerate(faces):
    for j in range(3):
      rec.vectors[i][j] = vertices[f[j],:]
  return rec

def main():
  print('Generating blank record.')
  record_mesh = calculaterecordshape()
  record_mesh.save(rpm + '_blank_lp.stl')
  
  # Create a new plot
  axes = mplot3d.Axes3D(pyplot.figure()) 
  axes.add_collection3d(mplot3d.art3d.Poly3DCollection(record_mesh.vectors))

  # Auto scale to the mesh size
  scale = cube_back.points.flatten()
  axes.auto_scale_xyz(scale, scale, scale)

  # Show the plot to the screen
  pyplot.show()

main()
