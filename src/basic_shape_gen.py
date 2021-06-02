import stl
from stl import mesh

import numpy as np
from cmath import tau
import math

from matplotlib import pyplot
from mpl_toolkits import mplot3d

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
  
  #Create vector lists
  outerEdgeUpper, outerEdgeLower = setzpos(generatecircumference(0, radius))
  centerHoleUpper, centerHoleLower = setzpos(generatecircumference(0, innerHole / 2))

  #Set faces
  faces = tristrip(centerHoleUpper, centerHoleLower)
  faces.append(tristrip(centerHoleLower, outerEdgeLower))
  faces.append(tristrip(outerEdgeLower, outerEdgeUpper))
  vertices = outerEdgeUpper.append(outerEdgeLower).append(centerHoleUpper).append(centerHoleLower) 

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
