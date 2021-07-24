import configparser
from math import pi


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


# Set 2pi
precision = 5
tau = 2 * pi

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
depth = truncate((6 * microns_per_layer) / 100, precision)
# calculcate angular incrementation amount
thetaIter = truncate((30 * samplingRate) / (DOWNSAMPLING * RPM), precision)
incrNum = truncate(tau / thetaIter, precision)
radIncr = truncate((groove_width + 2 * bevel * amplitude) / thetaIter,
                   precision)  # calculate radial incrementation amount
