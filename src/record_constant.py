# Define variables
import cmath.tau

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

class 3DShape:
    def __init__(self, f, xyz):
        self.f = f
        self.x, self.y, self.z = xyz

    def __str__(self):
        return ','.join([self.f, self.x, self.y, self.z])

