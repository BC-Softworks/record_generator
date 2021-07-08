#!/usr/bin/env python

import numpy as np
from math import cos, pow, sin, sqrt
import csv

# https://pypi.org/project/numpy-stl/
import stl
from stl import mesh

# Performance mesuring
import memory_profiler
import time

import record_globals as rg
from record_globals import *

from basic_shape_gen import setzpos, create_polygon, calculate_record_shape

#Outer Upper vertex
def ou(r, a, b, theta, rH) -> tuple:
  w = r + a * b
  return Vertex(w * cos(theta), w * sin(theta), rH)

#Inner Upper vertex
def iu(r, a, b, theta, rH) -> tuple:
  w = r - gW - a * b
  return Vertex(w * cos(theta), w * sin(theta), rH)

#Outer Lower vertex
def ol(r, theta, gH) -> tuple:
  return Vertex(r * cos(theta), r * sin(theta), gH)

#Inner Lower vertex
def il(r, theta, gH) -> tuple:
  w = r - gW
  return Vertex(w * cos(theta), w * sin(theta), gH)


def grooveHeight(audio_array, samplenum):
  baseline = rH-depth-amplitude
  return truncate(baseline*audio_array[int(rateDivisor*samplenum)], precision)

def draw_groove_cap(lastEdge, r, gH, shape):
  stop1 = [ou(r, amplitude, bevel, 0, rH), iu(r, amplitude, bevel, 0, rH)]
  stop2 = [ol(r, 0, gH), il(r, 0, gH)]
  shape.add_vertices(stop1 + stop2)

  #Draw triangles
  shape.tristrip(stop1,stop2)

  #Fill in around cap
  stop3 = [lastEdge[-1], (innerRad, r, rH)]
  shape.add_vertex(stop3[1])
  shape.tristrip(stop1, stop3)
  
  return shape

def fill_remaining_area(r, shape):
  remainingSpace = create_polygon(innerRad, 8, rH)
  edgeOfGroove = create_polygon(r, 8, rH)
  shape.add_vertices(remainingSpace + edgeOfGroove)
  remainingSpace.append(remainingSpace[0])
  edgeOfGroove.append(edgeOfGroove[0])
  shape.tristrip(remainingSpace, edgeOfGroove)
  return shape

# r is the radial postion of the vertex beign drawn
def draw_spiral(audio_array, r, shape = rg._3DShape(), info = True):

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

      gH = grooveHeight(audio_array, samplenum)
      outer = grooveOuterUpper + grooveOuterLower
      inner = grooveInnerUpper + grooveInnerLower
      shape.add_vertices(outer + inner)

      if index == 0:
          #Draw triangle to close outer part of record
          shape.tristrip(grooveOuterUpper, grooveOuterLower)
      else:
          shape.tristrip(grooveInnerUpper, grooveOuterLower)
      
      shape.tristrip(grooveOuterLower, grooveInnerLower)
      shape.tristrip(grooveInnerLower, grooveInnerUpper)
      lastEdge = grooveInnerUpper

      index += 1
      if(info):
          print("Groove drawn: {}".format(index))
      
  # Draw groove cap
  gH = grooveHeight(audio_array, samplenum)
  shape = draw_groove_cap(lastEdge, r, gH, shape)

  #Close remaining space between last groove and center hole
  shape = fill_remaining_area(r, shape)

  return shape

# Main function
def main(filename, stlname):

  # Read in array of bytes as float
  lst = [x for x in csv.reader(open(filename, 'rt', newline=''), delimiter=',')][0]
  lst = [float(x) for x in lst if x != '']

  # Normalize the values
  m = max(lst)
  lst = [truncate(abs(x) + m, precision) for x in lst]
  m *= 4
  normalizedDepth = [truncate(x / m, precision) for x in lst]
  
  print("Generate record shape")
  recordShape = calculate_record_shape(info = False)
  print("Drawing spiral object")
  shape = draw_spiral(normalizedDepth, outerRad, recordShape)
  print("Removing duplicate faces from shape spiral object")
  shape.remove_duplicate_faces()
  print("Removing empty faces from shape spiral object")
  shape.remove_empty_faces()
  print("Converting shape to mesh object")
  full_mesh = shape.shape_to_mesh()
  print("Saving mesh to " + "stl/" + stlname + ".stl")
  full_mesh.save("stl/" + stlname + ".stl", mode=stl.Mode.BINARY)

#Run program
if __name__ == '__main__':
  m1 = memory_profiler.memory_usage()
  t1 = time.process_time()
  main("audio/sample.csv", "sample_engraved")
  t2 = time.process_time()
  m2 = memory_profiler.memory_usage()
  time_diff = t2 - t1
  mem_diff = m2[0] - m1[0]
  print(f"It took {time_diff:.2f} Secs and {mem_diff:.2f} Mb to execute this method")
