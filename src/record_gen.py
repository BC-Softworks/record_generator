#!/usr/bin/env python

import pickle
import numpy as np
import math
import csv

import stl
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

import record_constant
from record_constant import *

from basic_shape_gen import setzpos 
from basic_shape_gen import generatecircumference

#Outer Upper vertex
def ou(r, a, b, theta, rH) -> tuple:
  w = r + a * b
  return (r + w * math.cos(theta), r + w * math.sin(theta), rH)

#Inner Upper vertex
def iu(r, a, b, theta, rH) -> tuple:
  w = r - grooveWidth - a * b
  return (r + w * math.cos(theta), r + w * math.sin(theta), rH)

#Outer Lower vertex
def ol(r, theta, gH) -> tuple:
  return (r + r * math.cos(theta), r + r * math.sin(theta), gH)

#Inner Lower vertex
def il(r, theta, gH) -> tuple:
  w = r - grooveWidth
  return (r + w * math.cos(theta), r + w * math.sin(theta), gH)

def grooveHeight(audio_array, samplenum):
  return truncate(recordHeight-depth-amplitude+audio_array[int(rateDivisor*samplenum)], precision);

def groove_cap(r, a, b, theta, rH, gH, shape):
  stop1 = [ou(r, a, b, theta, rH), iu(r, a, b, theta, rH)]
  stop2 = [ol(r, theta, gH), il(r, theta, gH)]

  #Draw triangles
  shape.triStrip(stop1,stop2);

# r is the radial postion of the vertex beign drawn
def draw_grooves(audio_array, r, shape = record_constant._3DShape()):

  # Print number of grooves to draw
  totalGrooveNum = len(audio_array) // (rateDivisor * thetaIter)

  #Inner while for groove position
  lastEdge = None
  index = samplenum = 0
  while rateDivisor*samplenum < (len(audio_array)-rateDivisor*thetaIter+1):
      grooveOuterUpper = []
      grooveOuterLower = []
      grooveInnerUpper = []
      grooveInnerLower = []

      theta = 0
      while theta < tau:
          gH = grooveHeight(audio_array, samplenum)
          grooveOuterUpper.append(ou(r, amplitude, bevel, theta, rH))
          grooveOuterLower.append(iu(r, amplitude, bevel, theta, rH))
          grooveInnerUpper.append(ol(r, theta, gH))
          grooveInnerLower.append(il(r, theta, gH))
          r -= radIncr
          theta += incrNum
          samplenum += 1

      
      outer = grooveOuterUpper + grooveOuterLower
      inner = grooveInnerUpper + grooveInnerLower
      lst = outer + inner

      for vertex in lst:
          #print(str(vertex) + " " + str(vertex in shape.get_vertices()))
          shape.add_vertex(vertex)

      lastEdge = inner #grooveInnerUpper
      #Connect verticies
      shape.tristrip(lastEdge, grooveOuterUpper)
      shape.tristrip(grooveOuterUpper, grooveOuterLower)
      shape.tristrip(grooveOuterLower, grooveInnerLower)
      shape.tristrip(grooveInnerLower, grooveInnerUpper)

      index += 1
      print("Groove drawn: {} of {}".format(index, int(totalGrooveNum)))
  # Draw groove cap
  theta = 0
  stop1 = [ou(r, amplitude, bevel, theta, rH), iu(r, amplitude, bevel, theta, rH)]
  stop2 = [ol(r, theta, gH), il(r, theta, gH)]
  cap = stop1 + stop2
  
  for i in range(0,4):
    shape.add_vertex(cap[i])

  #Draw triangles
  shape.tristrip(stop1,stop2);

  #Fill in around cap
  stop3 = [lastEdge[-1]]
  stop3.append((r+innerHole/2*math.cos(theta), r+innerHole/2*math.sin(theta), rH))
  shape.add_vertex(stop3[1])
  shape.tristrip(stop1, stop3)

  #Close remaining space between last groove and center hole
  remainingSpace, _ = setzpos(generatecircumference(0, innerHole / 2))
  for v in remainingSpace:
    shape.add_vertex(v)
  
  
  shape.tristrip(lastEdge, remainingSpace)

  return shape

def display_stl_mplot():
  axes = mplot3d.Axes3D(pyplot.figure())
  axes.add_collection3d(mplot3d.art3d.Poly3DCollection(com.vectors))

  # Show the plot to the screen
  pyplot.show()



# Main function
def main(filename, stlname, pickling=False):

  # Read in array of bytes as float
  lst = [x for x in csv.reader(open(filename, 'rt', newline=''), delimiter=',')][0]
  lst = [float(x) for x in lst if x != '']

  # Normalize the values
  m = max(lst) * 60
  normalizedDepth = [truncate(x / m, precision) for x in lst]

  shapefile = open("pickle/{}_shape.p".format(rpm), 'rb')
  recordShape = pickle.load(shapefile)
  shapefile.close()
  
  print("Pre-engraving vertices: " + str(len(recordShape.get_vertices())))
  print("Pre-engraving faces: " + str(len(recordShape.get_faces())))

  shape = draw_grooves(normalizedDepth, outerRad, recordShape)
  print("Done drawing grooves.\nTranslating grooves to mesh object.")

  faces = shape.get_faces()
  vertices = shape.get_vertices()
  full_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
  for i, f in enumerate(faces):
      for j in range(3):
          full_mesh.vectors[i][j] = vertices[f[j],:]
  
  print("Post-engraving vertices: " + str(len(vertices)))
  print("Post-engraving faces: " + str(len(faces)))

  print("Save mesh.")
  full_mesh.save("stl/" + stlname + ".stl")
  
  print("Done.")

#Run program
if __name__ == '__main__':
    #print("\n"); print_constants(); print("\n")
    main("audio/sample.csv", "sample_engraved")
