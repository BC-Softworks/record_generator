#!/usr/bin/env python

import pickle
import numpy as np
from math import cos, pow, sin, sqrt
import csv

# https://pypi.org/project/numpy-stl/
import stl
from stl import mesh

# Performance mesuring
import memory_profiler
import time

from record_globals import precision, tau, samplingRate,rpm, downsampling, thetaIter, diameter, radIncr, rateDivisor
from record_globals import radius, innerHole, innerRad, outerRad, rH, amplitude, depth, bevel, gW, incrNum
from record_globals import truncate, _3DShape

from basic_shape_gen import setzpos, circumference_generator, calculate_record_shape

# horizontial_modulation
def hm(x, y, gH):
  v0, v1 = radius - x,  radius - y
  m = sqrt(pow(v0, 2) + pow(v1, 2))
  h = (gH * (v0 / m), gH * (v1 / m), 0)
  return h

#Outer Upper vertex
def ou(r, a, b, theta, rH, gH) -> tuple:
  w = r + a * b
  x, y = w * cos(theta), w * sin(theta)
  v, h = (x, y, rH), hm(x, y, gH)
  return h[0] + v[0], h[1] + v[1], rH

#Inner Upper vertex
def iu(r, a, b, theta, rH, gH) -> tuple:
  w = r - gW - a * b
  x, y = w * cos(theta), w * sin(theta)
  v, h = (x, y, rH), hm(x, y, gH)
  return h[0] + v[0], h[1] + v[1], rH
  
#Outer Lower vertex
def ol(r, theta, gH) -> tuple:
  x, y = r * cos(theta), r * sin(theta)
  v, h = (x, y, gH), hm(x, y, gH)
  return h[0] + v[0], h[1] + v[1], rH - 0.05

#Inner Lower vertex
def il(r, theta, gH) -> tuple:
  w = r - gW
  x, y = r * cos(theta), r * sin(theta)
  v, h = (x, y, gH), hm(x, y, gH)
  return h[0] + v[0], h[1] + v[1], rH - 0.05


def grooveHeight(audio_array, samplenum):
  baseline = rH-depth-amplitude
  return truncate(baseline*audio_array[int(rateDivisor*samplenum)]/2, precision)

# r is the radial postion of the vertex beign drawn
def draw_spiral(audio_array, r, shape = _3DShape(), info = True):

  #Inner while for groove position
  lastEdge = None
  index = samplenum = 0
  gH = grooveHeight(audio_array, samplenum)

  s1 = [ou(radius, amplitude, bevel, 0, rH, gH), iu(radius, amplitude, bevel, 0, rH, gH)]
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
              grooveOuterUpper.append(ou(r, amplitude, bevel, theta, rH, gH))
          grooveOuterLower.append(iu(r, amplitude, bevel, theta, rH, gH))
          grooveInnerUpper.append(ol(r, theta, gH))
          grooveInnerLower.append(il(r, theta, gH))
          r -= radIncr
          theta += incrNum
          samplenum += 1

      gH = grooveHeight(audio_array, samplenum)
      outer = grooveOuterUpper + grooveOuterLower
      inner = grooveInnerUpper + grooveInnerLower
      shape.add_vertices(outer + inner)

      lastEdge = grooveOuterUpper if index == 0 else inner

      if index == 0:
          #Draw triangle to close outer part of record
          shape.tristrip(lastEdge, grooveOuterUpper)
          shape.tristrip(grooveOuterUpper, grooveOuterLower)
          
          #Complete beginning cap if necessary
          s1 = [ou(r, amplitude, bevel, theta, rH, gH), iu(r, amplitude, bevel, theta, rH, gH)]
          shape.add_vertices(s1)
          shape.tristrip(s1,s1)
      else:
          shape.tristrip(lastEdge, grooveOuterLower)
      
      shape.tristrip(grooveOuterLower, grooveInnerLower)
      shape.tristrip(grooveInnerLower, grooveInnerUpper)

      index += 1
      if(info):
          print("Groove drawn: {}".format(index))
      
  # Draw groove cap
  stop1 = [ou(r, amplitude, bevel, 0, rH, gH), iu(r, amplitude, bevel, 0, rH, gH)]
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
  remainingSpace = list(setzpos(circumference_generator(0, innerRad), rH))
  edgeOfGroove = list(setzpos(circumference_generator(0, r), rH))
  shape.add_vertices(remainingSpace + edgeOfGroove)
  shape.tristrip(remainingSpace, edgeOfGroove)

  return shape

# Main function
def main(filename, stlname):

  # Read in array of bytes as float
  lst = [x for x in csv.reader(open(filename, 'rt', newline=''), delimiter=',')][0]
  lst = [float(x) for x in lst if x != '']

  # Normalize the values
  m = pow(max(lst), 2)
  normalizedDepth = [truncate(x / m, precision) for x in lst]

  print("Generate record shape")
  recordShape = calculate_record_shape(info = False)

  print("Drawing spiral object")
  shape = draw_spiral(normalizedDepth, outerRad, recordShape)
  print("Removing duplicate faces from shape spiral object")
  shape.remove_duplicate_faces()
  print("Vertices: " + str(len(shape.get_vertices())))
  print("Faces: " + str(len(shape.get_faces())))
  print("Converting shape to mesh object")
  full_mesh = shape.shape_to_mesh()
  print("Saving mesh to " + "stl/" + stlname + ".stl")
  full_mesh.save("stl/" + stlname + ".stl", mode=stl.Mode.BINARY)

#Run program
if __name__ == '__main__':
  m1 = memory_profiler.memory_usage()
  t1 = time.process_time()
  main("audio/sample.csv", "Sample_engraved")
  t2 = time.process_time()
  m2 = memory_profiler.memory_usage()
  time_diff = t2 - t1
  mem_diff = m2[0] - m1[0]
  print(f"It took {time_diff:.2f} Secs and {mem_diff:.2f} Mb to execute this method")
