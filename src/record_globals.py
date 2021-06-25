from bidict import bidict
import numpy as np
from math import pi
import configparser
from collections import OrderedDict, namedtuple

# https://pypi.org/project/numpy-stl/
from stl import mesh
from stl import RemoveDuplicates



def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

# Set 2pi
precision = 5
tau = truncate(2 * pi, precision)

# Set global variable from constants file
config = configparser.ConfigParser()
config.read('record_constants.ini')

# Audio setting
samplingRate = int(config['Audio']['samplingRate'])
rpm = int(config['Audio']['rpm'])
downsampling = int(config['Audio']['downsampling'])

# Record dimensions
diameter = float(config['Record Dimensions']['diameter'])
radius = float(config['Record Dimensions']['radius'])
outerRad = float(config['Record Dimensions']['outerRad'])
innerRad = float(config['Record Dimensions']['innerRad'])
innerHole = float(config['Record Dimensions']['innerHole'])
rH = int(config['Record Dimensions']['recordHeight'])

# Groove dimensions
micronsPerLayer =  config['Groove Dimensions'].getfloat('micronsPerLayer')
bevel = config['Groove Dimensions'].getfloat('bevel')
gW = config['Groove Dimensions'].getfloat('grooveWidth')
rateDivisor = int(config['Groove Dimensions']['rateDivisor'])


thetaIter = truncate((60 * samplingRate) / (downsampling * rpm), precision)
# 24 is the amplitude of signal (in 16 micron steps)
amplitude = truncate((24 * micronsPerLayer) / 1000, precision)
# 6 is the measured in 16 microns steps, depth of tops of wave in groove from uppermost surface of record
depth = truncate((6 * micronsPerLayer) / 1000, precision)
incrNum = truncate(tau / thetaIter, precision) # calculcate angular incrementation amount
radIncr = truncate((gW + 2 * bevel * amplitude) / thetaIter, precision)  # calculate radial incrementation amount

Vertex = namedtuple('Vertex', 'x y z')
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
            self.vertices[index] = Vertex(*xyz)
            return index
        else:
            return -1 
    
    def add_vertices(self, lst):
      for v in lst:
          self.add_vertex(Vertex(*v))

    # It is faster to add all the faces and remove duplicates at the end
    # then to check after every add
    def add_face(self, point_a, point_b, point_c):
        points = [point_a, point_b, point_c]
        v = Vertex(*[self.vertices.inverse[x] for x in points])
        self.faces.append(v)
    
    def get_vertices(self):
        lst = [self.vertices[i] for i in range(0, len(self.vertices) )]
        return np.array(lst)
    
    def get_faces(self):
        return np.array(self.faces)

    def tristrip(self, a, b):
        l = min(len(a), len(b)) - 1
        for i in range(0, l):
            self.add_face(a[i], a[i+1], b[i])
            self.add_face(b[i], b[i+1], a[i+1])

    def remove_duplicate_faces(self):
        self.faces = list(OrderedDict.fromkeys(self.faces))
    
    def remove_empty_faces(self):
        self.faces = list(filter(lambda f: f[0] != f[1] and f[0] != f[2], self.faces))
    
    def shape_to_mesh(shape) -> mesh.Mesh:
      faces = shape.get_faces()
      vertices = shape.get_vertices()
      rec = mesh.Mesh(data=np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype), speedups=True)
      for i, f in enumerate(faces):
        for j in range(3):
          rec.vectors[i][j] = vertices[f[j],:]
      return rec
