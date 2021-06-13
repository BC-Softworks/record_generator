#!/usr/bin/env python

import pickle
import numpy as np
from math import cos, sin
import csv
import datetime

import stl
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

from record_globals import precision, tau, samplingRate,rpm, downsampling, thetaIter, diameter, radIncr, rateDivisor
from record_globals import radius, innerHole, innerRad, outerRad, rH, amplitude, depth, bevel, grooveWidth, incrNum
from record_globals import truncate, _3DShape

from basic_shape_gen import setzpos, shape_to_mesh, generatecircumference

#Outer Upper vertex
def ou(r, a, b, theta, rH) -> tuple:
  w = r + a * b
  return (r + w * cos(theta), r + w * sin(theta), rH)

#Inner Upper vertex
def iu(r, a, b, theta, rH) -> tuple:
  w = r - grooveWidth - a * b
  return (r + w * cos(theta), r + w * sin(theta), rH)

#Outer Lower vertex
def ol(r, theta, gH) -> tuple:
  return (r + r * cos(theta), r + r * sin(theta), gH)

#Inner Lower vertex
def il(r, theta, gH) -> tuple:
  w = r - grooveWidth
  return (r + w * cos(theta), r + w * sin(theta), gH)

def grooveHeight(audio_array, samplenum):
  baseline = rH-depth-amplitude
  return truncate(baseline+audio_array[int(rateDivisor*samplenum)], precision)

# r is the radial postion of the vertex beign drawn
def draw_spiral(audio_array, r, shape = _3DShape()):

  # Print number of grooves to draw
  totalGrooveNum = len(audio_array) // (rateDivisor * thetaIter)

  #Inner while for groove position
  lastEdge = None
  index = samplenum = 0
  gH = grooveHeight(audio_array, samplenum)

  s1 = [ou(radius, amplitude, bevel, 0, rH), iu(radius, amplitude, bevel, 0, rH)]
  s2 = [ol(radius, 0, gH), il(radius, 0, gH)]
  shape.add_vertices(s1 + s2)
  shape.tristrip(s1, s2)
  while rateDivisor*samplenum < (len(audio_array)-rateDivisor*thetaIter+1):
      grooveOuterUpper = []
      grooveOuterLower = []
      grooveInnerUpper = []
      grooveInnerLower = []

      theta = 0
      while theta < tau:
          gH = grooveHeight(audio_array, samplenum)
          if index == 0:
              grooveOuterUpper.append(ou(r, amplitude, bevel, theta, rH))
          grooveOuterLower.append(iu(r, amplitude, bevel, theta, rH))
          grooveInnerUpper.append(ol(r, theta, gH))
          grooveInnerLower.append(il(r, theta, gH))
          r -= radIncr
          theta += incrNum
          samplenum += 1

      outer = grooveOuterUpper + grooveOuterLower
      inner = grooveInnerUpper + grooveInnerLower
      shape.add_vertices(outer + inner)

      lastEdge = grooveOuterUpper if index == 0 else inner

      if index == 0:
          #Draw triangle to close outer part of record
          shape.tristrip(lastEdge, grooveOuterUpper)
          shape.tristrip(grooveOuterUpper, grooveOuterLower)
          
          #Complete beginning cap if necessary
          s1 = [ou(r, amplitude, bevel, theta, rH), iu(r, amplitude, bevel, theta, rH)]
          shape.add_vertices(s1)
          shape.tristrip(s1,s1)
      else:
          shape.tristrip(lastEdge, grooveOuterLower)
      
      shape.tristrip(grooveOuterLower, grooveInnerLower)
      shape.tristrip(grooveInnerLower, grooveInnerUpper)

      index += 1
      print("Groove drawn: {} of {}".format(index, int(totalGrooveNum)))
      
  # Draw groove cap
  stop1 = [ou(r, amplitude, bevel, 0, rH), iu(r, amplitude, bevel, 0, rH)]
  stop2 = [ol(r, 0, gH), il(r, 0, gH)]
  cap = stop1 + stop2
  shape.add_vertices(cap)

  #Draw triangles
  shape.tristrip(stop1,stop2)

  #Fill in around cap
  stop3 = [lastEdge[-1], (r+innerRad, r, rH)]
  shape.add_vertex(stop3[1])
  shape.tristrip(stop1, stop3)

  #Close remaining space between last groove and center hole
  remainingSpace, _ = setzpos(generatecircumference(0, innerRad))
  edgeOfGroove, _ = setzpos(generatecircumference(0, r))
  shape.add_vertices(remainingSpace + edgeOfGroove)

  shape.tristrip(remainingSpace, edgeOfGroove)

  return shape

# Main function
def main(filename, stlname):

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

  ## For debugging
  # shape_to_mesh(draw_spiral(normalizedDepth, outerRad, recordShape)).save("grooves.stl")

  shape = draw_spiral(normalizedDepth, outerRad, recordShape)
  full_mesh = shape_to_mesh(shape)

  full_mesh.save("stl/" + stlname + ".stl", mode=stl.Mode.BINARY)

#Run program
if __name__ == '__main__':
    now = datetime.datetime.now()
    main("audio/sample.csv", "sample_engraved")
    print("Time taken: " + str(datetime.datetime.now() - now)[5:9])
