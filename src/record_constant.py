# Define variables
from bidict import bidict
import numpy as np
import math


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

precision = 5
tau = truncate(2 * math.pi, precision)
samplingRate = 44100 # 44.1khz audio
rpm = 45
downsampling = 4
thetaIter = truncate((60 * samplingRate) / (downsampling * rpm),precision)
diameter = 7 # diameter of record in inches
radius = diameter / 2 # radius of record inches
innerHole = 1 # For 33 1/3 rpm 0.286 # diameter of center hole in inches
innerRad = truncate(47/20, precision) # radius of innermost groove in inches
outerRad = truncate(23/4, precision)  # radius of outermost groove in inches
recordHeight = rH = truncate(1/8, precision)
micronsPerInch = 25400
micronsPerLayer = 16 # microns per vertical print layer
amplitude = truncate((24 * micronsPerLayer) / micronsPerInch, precision) # 24 is the amplitude of signal (in 16 micron steps)
depth = truncate((6 * micronsPerLayer) / micronsPerInch, precision) # 6 is the measured in 16 microns steps, depth of tops of wave in groove from uppermost surface of record
bevel = 0.5 # bevelled groove edge
grooveWidth = truncate(1/300, precision) # in 600dpi pixels
incrNum = truncate(tau / thetaIter, precision) # calculcate angular incrementation amount
radIncr = truncate((grooveWidth + 2 * bevel * amplitude) / thetaIter, precision)  # calculate radial incrementation amount
rateDivisor = 4.0 # Not sure what this should be yet

def print_constants():
    print("Record constants")
    print("samplingRate: {}".format(samplingRate))
    print("rpm: {}".format(rpm))
    print("downsampling: {}".format(downsampling))
    print("thetaIter: {}".format(thetaIter))
    print("diameter: {}".format(diameter))
    print("radius: {}".format(radius))
    print("innerHole: {}".format(innerHole))
    print("innerRad: {}".format(innerRad))
    print("outerRad: {}".format(outerRad))
    print("recordHeight: {}".format(recordHeight))
    print("micronsPerInch: {}".format(micronsPerInch))
    print("micronsPerLayer: {}".format(micronsPerLayer))
    print("amplitude: {}".format(amplitude))
    print("depth: {}".format(depth))
    print("bevel: {}".format(bevel))
    print("grooveWidth: {}".format(grooveWidth))
    print("incrNum: {}".format(incrNum))
    print("radIncr: {}".format(radIncr))
    print("rateDivisor: {}".format(rateDivisor))


class _3DShape:
    def __init__(self, dict={}):
        self.vertices = bidict(dict)
        self.faces = []

    def __str__(self):
        return self.vertices

    def add_vertex(self, xyz) -> int:
        assert len(xyz) == 3 #;print(xyz)
        index = len(self.vertices)
        if xyz not in self.vertices.inverse: 
            self.vertices[index] = xyz
            return index
        else:
            return -1 #self.get_vertices().tolist().index(xyz)

    def add_face(self, point_a, point_b, point_c):
        points = [point_a, point_b, point_c]
        self.faces.append([self.vertices.inverse[x] for x in points])
    
    def get_vertices(self):
        lst = [self.vertices[i] for i in range(0, len(self.vertices) )]
        return np.array(lst)
    
    def get_faces(self):
        return np.array(self.faces)

    def tristrip(self, a, b):
        assert isinstance(a, list)
        assert isinstance(b, list)

        for i in range(0, len(min([a, b])) - 1):
            self.add_face(a[i], a[i+1], b[i])
            self.add_face(b[i], b[i+1], a[i+1])

