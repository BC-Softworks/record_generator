from cmath import tau
import numpy as np
import math

import stl
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

from record_constant import *

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
    _solid.points[:, items] += multiplier * (step + padding)


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
###

#Outer Upper vertex
def ou(r, a, b, theta, rH):
  w = r + a * b
  return np.array([r + w * cos(theta), r + w * sin(theta), rH])

#Inner Upper vertex
def iu(r, a, b, theta, rH):
  w = r - gW - a * b
  return np.array([r + w * cos(theta), r + w * sin(theta), rH])

#Outer Lower vertex
def ol(r, a, theta, gH):
  return np.array([r + r * cos(theta), r + r * sin(theta), gH])

#Inner Lower vertex
def il(r, a, theta, gH):
  w = r - gW
  return np.array([r + w * cos(theta), r + w * sin(theta), gH])

def grooveHeight(audio_array):
  return recordHeight-depth-amplitude+audio_array[rateDivisor*samplenum];

def groove_cap(r, a, b, theta, rH, gH):
  stop1 = np.array([ou(r, a, b, theta, rH), iu(r, a, b, theta, rH)])
  stop2 = np.array([ol(r, a, b, theta, gH), il(r, a, theta, gH)])
  
  #Draw triangles
  geo.quadStrip(stop1,stop2);

# r is the radial postion of the vertex beign drawn
def draw_grooves(audio_array, r):
  #ti is thetaIter
  baseCase = lambda ti : rateDivisor*samplenum < (lens(audio_array)-rateDivisor*ti+1)
               and r > innerRad
  
  if baseCase(thetaIter):
    grooveOuterUpper = []
    grooveOuterLower = []
    grooveInnerUpper = []
    grooveInnerLower = []
    for theta in range(0, incrNum, tau):
      samplenum += 1
      gH = grooveHeight(audio_array)      
      grooveOuterUpper.append(ou(r, a, b, theta, rH))
      grooveOuterLower.append(iu(r, a, b, theta, rH))
      grooveInnerUpper.append(ol(r, a, theta, gH))
      grooveInnerLower.append(il(r, a, theta, gH))
      r -= radIncr

    #Connect verticies
    geo.quadStrip(lastEdge, grooveOuterUpper)
    geo.quadStrip(grooveOuterUpper, grooveOuterLower)
    geo.quadStrip(grooveOuterLower, grooveInnerLower)
    geo.quadStrip(grooveInnerLower, grooveInnerUpper)
    

    draw_grooves(audio_array, r)
  
  # Draw groove cap
  else:
 
    stop1 = np.array([ou(r, a, b, theta, rH), iu(r, a, b, theta, rH)])
    stop2 = np.array([ol(r, a, b, theta, gH), il(r, a, theta, gH)])

    #Draw triangles
    geo.quadStrip(stop1,stop2);
 
    #InnerUpper[0]
    stop3 = [grooveInnerUpper.first()]
    #Innerhole[0]
    stop3.append(radius+innerHole/2*cos(theta),radius+innerHole/2*sin(theta),recordHeight)
    
    #Draw triangles
    geo.quadStrip(stop1,stop3)

    #Close remaining space between last groove and center hole  
    geo.quadStrip(lastEdge,recordHoleUpper)

# Main function  
def main(filename):
  
  # Read in array of bytes as floats
  arr = np.asarray(open(filename, 'rt', newline='').read().partition(','), dtype='numpy.single')
  # Normalize the values
  arr = np.divide(arr, np.amax(arr))
  totalGrooveNum = lens(normalizedDepth) // (rateDivisor * thetaIter)

  #Import blank record
  record_mesh = mesh.Mesh.from_file(rpm + 'BlankLP.stl')

  print("Grooves to draw {}.".format(totalGrooveNum))
  mesh = draw_grooves(normalizedDepth)
  print("Done.")

  # Create a new plot
  # Load the STL files and add the vectors to the plot
  # Auto scale to the mesh size
  
  axes = mplot3d.Axes3D(pyplot.figure())
  axes.add_collection3d(mplot3d.art3d.Poly3DCollection(mesh.vectors))
  scale = your_mesh.points.flatten()
  axes.auto_scale_xyz(scale, scale, scale)

  # Show the plot to the screen
  pyplot.show()

#Run program  
main("Jazz-Example.csv")
