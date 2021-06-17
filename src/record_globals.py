from bidict import bidict
import numpy as np
from math import pi

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

precision = 5
tau = truncate(2 * pi, precision)
samplingRate = 44100 # 44.1khz audio
rpm = 45
downsampling = 1.5 #4
thetaIter = truncate((60 * samplingRate) / (downsampling * rpm), precision)
diameter = 90 #175.41875 # diameter of record in mm
radius = diameter / 2 # radius of record mm
innerHole = 38.2524 # For 33 1/3 rpm 0.286 # diameter of center hole in mm
innerRad = truncate(45, precision) # radius of innermost groove in mm
outerRad = truncate(89.5, precision) # truncate(170, precision)  # radius of outermost groove in mm
rH = truncate(8, precision)
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


class _3DShape:
    def __init__(self, dict={}):
        self.vertices = bidict(dict)
        self.faces = []

    def __str__(self):
        return str(self.vertices)

    def add_vertex(self, xyz) -> int:
        assert len(xyz) == 3 #;print(xyz)
        index = len(self.vertices)
        if xyz not in self.vertices.inverse: 
            self.vertices[index] = xyz
            return index
        else:
            return -1 
    
    def add_vertices(self, lst):
      for vertex in lst:
          self.add_vertex(vertex)

    def add_face(self, point_a, point_b, point_c):
        points = [point_a, point_b, point_c]
        self.faces.append([self.vertices.inverse[x] for x in points])
    
    def get_vertices(self):
        lst = [self.vertices[i] for i in range(0, len(self.vertices) )]
        return np.array(lst)
    
    def get_faces(self):
        return np.array(self.faces)

    def tristrip(self, a, b):
        for i in range(0, min(len(a), len(b)) - 1):
            self.add_face(a[i], a[i+1], b[i])
            self.add_face(b[i], b[i+1], a[i])
