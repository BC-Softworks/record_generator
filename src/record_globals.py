from bidict import bidict
import numpy as np
from math import pi
import configparser
from collections import OrderedDict, namedtuple

# https://pypi.org/project/numpy-stl/
from stl import mesh

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
RPM = int(config['Audio']['rpm'])
DOWNSAMPLING = int(config['Audio']['downsampling'])

# Record dimensions
DIAMETER = float(config['Record Dimensions']['diameter'])
RADIUS = float(config['Record Dimensions']['radius'])
outer_rad = float(config['Record Dimensions']['outerRad'])
inner_rad = float(config['Record Dimensions']['innerRad'])
inner_hole = float(config['Record Dimensions']['innerHole'])
record_height = int(config['Record Dimensions']['recordHeight'])

# Groove dimensions
microns_per_layer = config['Groove Dimensions'].getfloat('micronsPerLayer')
bevel = config['Groove Dimensions'].getfloat('bevel')
groove_width = config['Groove Dimensions'].getfloat('grooveWidth')
rate_divisor = int(config['Groove Dimensions']['rateDivisor'])

# 24 is the amplitude of signal (in 16 micron steps)
amplitude = truncate((24 * microns_per_layer) / 1000, precision)
# 6 is the measured in 16 microns steps, depth of tops of wave in groove from uppermost surface of record
depth = truncate((6 * microns_per_layer) / 1000, precision)
# calculcate angular incrementation amount
thetaIter = truncate((30 * samplingRate) / (DOWNSAMPLING * RPM), precision)
incrNum = truncate(tau / thetaIter, precision)
radIncr = truncate((groove_width + 2 * bevel * amplitude) / thetaIter,
                   precision)  # calculate radial incrementation amount

Vertex = namedtuple('Vertex', 'x y z')


class TriMesh():
    def __init__(self, dictionary={}):
        self.vertices = bidict(dictionary)
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
        lst = [self.vertices[i] for i in range(0, len(self.vertices))]
        return np.array(lst)

    def get_faces(self):
        return np.array(self.faces)

    def tristrip(self, list_a, list_b):
        lst = min(len(list_a), len(list_b)) - 1
        for i in range(0, lst):
            self.add_face(list_a[i], list_a[i + 1], list_b[i])
            self.add_face(list_b[i], list_b[i + 1], list_a[i + 1])

    def remove_duplicate_faces(self):
        self.faces = list(OrderedDict.fromkeys(self.faces))

    def remove_empty_faces(self):
        self.faces = list(
            filter(
                lambda f: f[0] != f[1] and f[0] != f[2],
                self.faces))

    def shape_to_mesh(self) -> mesh.Mesh:
        vertices = self.get_vertices()
        number_of_faces = len(self.faces)
        rec = mesh.Mesh(
            data=np.zeros(number_of_faces, dtype=mesh.Mesh.dtype), speedups=True)
        for f in range(number_of_faces):
            for j in range(3):
                rec.vectors[f][j] = vertices[self.faces[f][j], :]
        return rec
