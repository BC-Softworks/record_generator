#!/usr/bin/env python3

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

## From basic_shape_gen

# Generate circumference of record
# Recursive call comes first to to order of evaluation
def generatecircumference(t, r) -> list:
  lst = []
  while t < record_constant.tau:
    lst.append([radius + r * math.sin(t), radius + r * math.cos(t)])
    # Increasing incrNum for circumference to speed up processing
    # and shave off vertices unnecessary vertices
    # Consider creating seperate constant in record_constant for this function
    t += truncate(incrNum * 35, precision)

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

##
## From https://pypi.org/project/numpy-stl/
# Slightly optimized
# find the max dimensions, so we can know the bounding box, getting the height,
# width, length (because these are the step size)...
def find_mins_maxs(obj):
    return obj.x.min(), obj.x.max(), obj.y.min(), obj.y.max(), obj.z.min(), obj.z.max()


def translate(_solid, step, padding, multiplier, axis):
    if 'x' == axis:
        items = 0, 3, 6
    elif 'y' == axis:
        items = 1, 4, 7
    elif 'z' == axis:
        items = 2, 5, 8
    else:
        raise RuntimeError('Unknown axis %r, expected x, y or z' % axis)

    # _solid.points.shape == [:, ((x, y, z), (x, y, z), (x, y, z))]
    _solid.points[:, items] += (multiplier * step) + (multiplier * padding)


def copy_obj(obj, dims, num_rows, num_cols, num_layers):
    w, l, h = dims
    copies = []
    for layer in range(num_layers):
        for row in range(num_rows):
            for col in range(num_cols):
                _copy = mesh.Mesh(obj.data.copy())
                # pad the space between objects by 10% of the dimension being
                # translated
                if col != 0:
                    translate(_copy, w, w / 10.0, col, 'x')
                if row != 0:
                    translate(_copy, l, l / 10.0, row, 'y')
                if layer != 0:
                    translate(_copy, h, h / 10.0, layer, 'z')
                copies.append(_copy)
    return copies

def combine(m1, m2) -> mesh.Mesh:
    minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(m1)
    w1, l1, h1 = (maxx - minx, maxy - miny, maxz - minz)
    copies = copy_obj(m1, (w1, l1, h1), 2, 2, 1)

    # I wanted to add another related STL to the final STL
    minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(m2)
    w2, l2, h2 = (maxx - minx, maxy - miny, maxz - minz)
    translate(m2, w1, w1 / 10., 3, 'x')
    copies2 = copy_obj(m2, (w2, l2, h2), 2, 2, 1)
    return mesh.Mesh(np.concatenate([m1.data, m2.data] +
                                       [copy.data for copy in copies] +
                                       [copy.data for copy in copies2]))
###


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
  return truncate(recordHeight-depth-amplitude+audio_array[int(rateDivisor*samplenum)], 4);

def groove_cap(r, a, b, theta, rH, gH, shape):
  stop1 = [ou(r, a, b, theta, rH), iu(r, a, b, theta, rH)]
  stop2 = [ol(r, theta, gH), il(r, theta, gH)]

  #Draw triangles
  shape.triStrip(stop1,stop2);

# r is the radial postion of the vertex beign drawn
def draw_grooves(audio_array, r, shape = record_constant._3DShape()):
  #ti is thetaIter
  #Got rid of recusion because the BDFL said so
  #People wonder will I can't stand the dutch
  #Lowercase ducth because I don't have the respect to capitalize the proper noun


  # Print number of grooves to draw
  totalGrooveNum = len(audio_array) // (rateDivisor * thetaIter)

  #Inner while for groove position
  lastEdge = None
  samplenum = 0
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

      lastEdge = grooveInnerUpper
      #Connect verticies
      shape.tristrip(lastEdge, grooveOuterUpper)
      shape.tristrip(grooveOuterUpper, grooveOuterLower)
      shape.tristrip(grooveOuterLower, grooveInnerLower)
      shape.tristrip(grooveInnerLower, grooveInnerUpper)

      print("Groove drawn: {} of {}".format((samplenum//14701), int(totalGrooveNum)))
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
  stop3 = [grooveInnerUpper[0]]
  stop3.append((r+innerHole/2*math.cos(theta), r+innerHole/2*math.sin(theta), rH))
  shape.add_vertex(stop3[0])
  shape.add_vertex(stop3[1])
  shape.tristrip(stop1, stop3)

  #Close remaining space between last groove and center hole
  remainingSpace, _ = setzpos(generatecircumference(0, innerHole / 2))
  for v in remainingSpace + lastEdge:
    shape.add_vertex(v)
  shape.tristrip(lastEdge, remainingSpace)

  return shape

def display_stl():
  axes = mplot3d.Axes3D(pyplot.figure())
  axes.add_collection3d(mplot3d.art3d.Poly3DCollection(com.vectors))

  # Show the plot to the screen
  pyplot.show()

# Main function
def main(filename, pickling=False):

  # Read in array of bytes as float
  lst = [x for x in csv.reader(open(filename, 'rt', newline=''), delimiter=',')][0]
  lst = [float(x) for x in lst if x != '']

  # Normalize the values
  m = max(lst) * 60
  normalizedDepth = [truncate(x / m, precision) for x in lst]

  if(pickling == True):
      shapefile = open("pickle/{}_shape.p".format(rpm), 'rb')
      recordShape = pickle.load(shapefile)
      shapefile.close()
      
      print("Pre-engraving vertices: " + str(len(recordShape.get_vertices())))
      print("Pre-engraving faces: " + str(len(recordShape.get_faces())))

      shape = draw_grooves(normalizedDepth, radius - 0.2, recordShape)
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
      full_mesh.save("stl/" + "disc_test_grooves" + ".stl")
  # Combing is currenttly broken
  else:
      #Import blank record
      print("Import preprocessed blank " + str(rpm) + " disc.")
      record_mesh = mesh.Mesh.from_file("stl/{}_disc.stl".format(rpm))
      #Draw groove
      shape = draw_grooves(normalizedDepth, radius - 0.2)
      print("Done drawing grooves.\nTranslating grooves to mesh object.")

      faces = shape.get_faces()
      vertices = shape.get_vertices()
      
      print("Vertices: " + str(len(vertices)))
      print("Faces: " + str(len(faces)))

      groove_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
      for i, f in enumerate(faces):
          for j in range(3):
              groove_mesh.vectors[i][j] = vertices[f[j],:]

      print("Save groove mesh for debugging")
      groove_mesh.save("stl/" + "grooves" + ".stl")
      print("Combining record and groove mesh")
      com = combine(record_mesh, groove_mesh)
      com.save("stl/" + "disc_test_grooves" + ".stl")
  print("Done.")

#Run program
if __name__ == '__main__':
    main("audio/sine.csv", True)
