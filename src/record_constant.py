# Define variables
from bidict import bidict
import numpy as np
import math

tau = 2 * math.pi
samplingRate = 44100 # 44.1khz audio
rpm = 45
downsampling = 4
thetaIter = (60 * samplingRate) / (downsampling * rpm)
diameter = 7 # diameter of record in inches
radius = diameter / 2 # radius of record inches
innerHole = 143/500 # diameter of center hole in inches
innerRad = 47/20 # radius of innermost groove in inches
outerRad = 23/4 # radius of outermost groove in inches
recordHeight = rH = 1/25
micronsPerInch = 25400
micronsPerLayer = 16 # microns per vertical print layer
amplitude = (24 * micronsPerLayer) / micronsPerInch # 24 is the amplitude of signal (in 16 micron steps)
depth = (6 * micronsPerLayer) / micronsPerInch # 6 is the measured in 16 microns steps, depth of tops of wave in groove from uppermost surface of record
bevel = 0.5 # bevelled groove edge
grooveWidth = 1/300 # in 600dpi pixels
incrNum = tau / thetaIter # calculcate angular incrementation amount
radIncr = (grooveWidth + 2 * bevel * amplitude) / thetaIter  # calculate radial incrementation amount
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
    print("recordHeight {}".format(recordHeight))
    print("micronsPerInch {}".format(micronsPerInch))
    print("micronsPerLayer {}".format(micronsPerLayer))
    print("amplitude {}".format(amplitude))
    print("depth {}".format(depth))
    print("bevel {}".format(bevel))
    print("grooveWidth {}".format(grooveWidth))
    print("incrNum {}".format(incrNum))
    print("radIncr {}".format(radIncr))
    print("rateDivisor: {}".format(rateDivisor))

class _3DShape:
    def __init__(self, dict={}):
        self.vertices = bidict(dict)
        self.faces = []

    def __str__(self):
        return self.vertices

    def add_vertex(self, xyz):
        index = len(self.vertices)
        self.vertices[index] = xyz
        return index

    def add_face(self, point_a, point_b, point_c):
        points = [self.point_a, self.point_b, self.point_c]
        self.faces.append([vertices.inverse[x] for x in points])
    
    def get_vertices(self):
        lst = [self.vertices[i] for i in range(0, len(self.vertices))]
        return np.array(lst)
    
    def get_faces(self):
        return np.array(self.faces)

