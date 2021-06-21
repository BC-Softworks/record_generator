from bidict import bidict
import numpy as np
from math import pi
from collections import OrderedDict
from itertools import permutations

# https://pypi.org/project/numpy-stl/
from stl import mesh

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

precision = 5
tau = truncate(2 * pi, precision)
samplingRate = 44100 # 44.1khz audio
rpm = 45
downsampling = 8 # 2.9696 optimal
thetaIter = truncate((60 * samplingRate) / (downsampling * rpm), precision)
diameter = 170 # diameter of record in mm
radius = diameter // 2 # radius of record mm
outerRad = truncate(75, precision) # truncate(170, precision)  # radius of outermost groove in mm
innerRad = truncate(25, precision) # radius of innermost groove in mm
innerHole = 38.2524 # For 33 1/3 rpm 0.286 inch # diameter of center hole in mm
rH = truncate(5, precision)
micronsPerLayer = 16 # microns per vertical print layer
# 24 is the amplitude of signal (in 16 micron steps)
amplitude = truncate((24 * micronsPerLayer) / 1000, precision)
# 6 is the measured in 16 microns steps, depth of tops of wave in groove from uppermost surface of record
depth = truncate((6 * micronsPerLayer) / 1000, precision)
bevel = 0.5 # bevelled groove edge
gW = truncate(0.05588, precision) # in 600dpi pixels grooveWidth
incrNum = truncate(tau / thetaIter, precision) # calculcate angular incrementation amount
radIncr = truncate((gW + 2 * bevel * amplitude) / thetaIter, precision)  # calculate radial incrementation amount
rateDivisor = 4.0 # Not sure what this should be yet


class _3DShape():
    def __init__(self, dict={}):
        self.vertices = bidict(dict)
        self.faces = []

    def __str__(self):
        return str(self.vertices)

    def add_vertex(self, xyz) -> int:
        assert len(xyz) == 3
        index = len(self.vertices)
        if xyz not in self.vertices.inverse: 
            self.vertices[index] = xyz
            return index
        else:
            return -1 
    
    def add_vertices(self, lst):
      for vertex in lst:
          self.add_vertex(vertex)
          
          
    # It is faster to add all the faces and remove duplicates at the end
    # then to check after every add
    def add_face(self, point_a, point_b, point_c):
        points = [point_a, point_b, point_c]
        tup = tuple([self.vertices.inverse[x] for x in points])
        
        self.faces.append(tup)
    
    def get_vertices(self):
        lst = [self.vertices[i] for i in range(0, len(self.vertices) )]
        return np.array(lst)
    
    def get_faces(self):
        return np.array(self.faces)

    def tristrip(self, a, b):
        for i in range(0, min(len(a), len(b)) - 1):
            self.add_face(a[i], a[i+1], b[i])
            self.add_face(b[i], b[i+1], a[i])

    def remove_duplicate_faces(self):
        self.faces = list(OrderedDict.fromkeys(self.faces))
        
    def shape_to_mesh(shape) -> mesh.Mesh:
      faces = shape.get_faces()
      vertices = shape.get_vertices()
      rec = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
      for i, f in enumerate(faces):
        for j in range(3):
          rec.vectors[i][j] = vertices[f[j],:]
      return rec
