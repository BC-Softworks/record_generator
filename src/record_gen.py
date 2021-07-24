#!/usr/bin/env python

from math import cos, sin
import csv

# Performance mesuring
import time
import memory_profiler

# https://pypi.org/project/numpy-stl/
import stl

import record_globals as rg
import trimesh as tm

from basic_shape_gen import create_polygon, calculate_record_shape


def outer_upper_vertex(rad, amp, bev, theta) -> tm.Vertex:
    width = rad + amp * bev
    return tm.Vertex(width * cos(theta), width * sin(theta), rg.record_height)


def inner_upper_vertex(rad, amp, bev, theta) -> tm.Vertex:
    width = rad - rg.groove_width + amp * bev
    return tm.Vertex(width * cos(theta), width * sin(theta), rg.record_height)


def outer_lower_vertex(rad, theta, g_h) -> tm.Vertex:
    return tm.Vertex(rad * cos(theta), rad * sin(theta), g_h)


def inner_lower_vertex(rad, theta, g_h) -> tm.Vertex:
    w = rad - rg.groove_width
    return tm.Vertex(w * cos(theta), w * sin(theta), g_h)


def groove_height(audio_array, sample_num):
    """Height of the groove extracted from the audio array"""
    baseline = rg.record_height - rg.depth
    amp = audio_array[int(rg.rate_divisor * sample_num)]
    return rg.truncate( baseline + amp, rg.precision)

def starting_cap(gH, shape):
    s1 = [outer_upper_vertex(rg.RADIUS, rg.amplitude, rg.bevel, 0),
          inner_upper_vertex(rg.RADIUS, rg.amplitude, rg.bevel, 0)]
    s2 = [outer_lower_vertex(rg.RADIUS, 0, gH), inner_lower_vertex(rg.RADIUS, 0, gH)]
    shape.quadstrip(s1, s2)
    return shape

def draw_groove_cap(last_edge, rad, height, trimesh):
    """Draws the ramp between the groove and inner cap"""
    stop1 = [outer_upper_vertex(rad, rg.amplitude, rg.bevel, 0),
             inner_upper_vertex(rad, rg.amplitude, rg.bevel, 0)]
    stop2 = [outer_lower_vertex(rad, 0, height), inner_lower_vertex(rad, 0, height)]
    trimesh.quadstrip(stop1, stop2)

    # Fill in around cap
    stop3 = [last_edge[-1], tm.Vertex(rg.inner_rad, rad, rg.record_height)]
    trimesh.add_vertex(stop3[1])
    trimesh.quadstrip(stop1, stop3)

    return trimesh


def fill_remaining_area(r, shape, edge_num=32):
    """Fill the space between the last groove and the center hole"""
    remaining_space = create_polygon(rg.inner_rad, edge_num, rg.record_height)
    edge_of_groove = create_polygon(r, edge_num, rg.record_height)
    remaining_space.append(remaining_space[0])
    edge_of_groove.append(edge_of_groove[0])
    shape.quadstrip(remaining_space, edge_of_groove)
    return shape


def draw_spiral(samplenum, audio_array, index, rad, gH, shape, info):
    arr_length = len(audio_array)
    while rg.rate_divisor * samplenum < (arr_length - rg.rate_divisor * rg.thetaIter + 1):
        groove_outer_upper = []
        groove_outer_lower = []
        groove_inner_upper = []
        groove_inner_lower = []

        theta = 0
        while theta < rg.tau:
            gH = groove_height(audio_array, samplenum)
            if index == 0:
                groove_outer_upper.append(outer_upper_vertex(rad, rg.amplitude, rg.bevel, theta))
            groove_outer_lower.append(inner_upper_vertex(rad, rg.amplitude, rg.bevel, theta))
            groove_inner_upper.append(outer_lower_vertex(rad, theta, gH))
            groove_inner_lower.append(inner_lower_vertex(rad, theta, gH))
            rad -= rg.radIncr
            theta += rg.incrNum
            samplenum += 1

        gH = groove_height(audio_array, samplenum)
        if index == 0:
            # Draw triangle to close outer part of record
            shape.quadstrip(groove_outer_upper, groove_outer_lower)
        else:
            shape.quadstrip(groove_inner_upper, groove_outer_lower)

        shape.quadstrip(groove_outer_lower, groove_inner_lower)
        shape.quadstrip(groove_inner_lower, groove_inner_upper)
        last_edge = groove_inner_upper

        index += 1
        if info:
            print("Groove drawn: {}".format(index))
    return samplenum, last_edge, rad

def draw_grooves(audio_array, rad, trimesh=tm.TriMesh(), info=True):
    """rad is the radial postion of the vertex beign drawn"""

    # Inner while for groove position
    last_edge = None
    index = 0
    samplenum = 0
    gH = groove_height(audio_array, samplenum)

    starting_cap(gH, trimesh)

    samplenum, last_edge, rad = draw_spiral(samplenum, audio_array, index, rad, gH, trimesh, info)

    # Draw groove cap
    gH = groove_height(audio_array, samplenum)
    trimesh = draw_groove_cap(last_edge, rad, gH, trimesh)

    # Close remaining space between last groove and center hole
    return fill_remaining_area(rad, trimesh)

def normalize_audio_data(filename):
    # Read in array of bytes as float
    audio_file = open(filename, 'rt', newline='')
    lst = [x for x in csv.reader(audio_file, delimiter=',')][0]
    lst = [float(x) for x in lst if x != '']

    # Normalize the values
    current_max = max(lst)
    lst = [rg.truncate(abs(x) + current_max, rg.precision) for x in lst]
    current_max *= 8
    normalized_depth = [rg.truncate(x / current_max, rg.precision) for x in lst]
    return normalized_depth

def main(filename, stlname):

    # Read in array of bytes as float
    normalized_depth = normalize_audio_data(filename)

    print("Generate record shape")
    disc_mesh = calculate_record_shape(info=False)
    disc_characteristic = disc_mesh.euler_characteristic()

    # Save for debugging
    disc_mesh.trimesh_to_npmesh().save('stl/disc_debug.stl', mode=stl.Mode.BINARY)
    
    # Draw grooves
    print("Drawing spiral object")
    groove_mesh = draw_grooves(normalized_depth, rg.outer_rad)
    groove_characteristic = groove_mesh.euler_characteristic()

    # Save for debugging
    groove_mesh.trimesh_to_npmesh().save('stl/grooves_debug.stl', mode=stl.Mode.BINARY)

    # Merge disc and grooves
    print("Merge objects")
    trimesh = disc_mesh.merge(groove_mesh)
    
    # Explicit clean up of the groove mesh
    # Saves ~3Mbs of ram
    del groove_mesh

    print('Checking merged mesh for errors')
    if trimesh.euler_characteristic() != groove_characteristic + disc_characteristic:
        print('Merge failed')
    
    print("Removing duplicate faces from trimesh")
    trimesh.remove_duplicate_faces()
    print("Removing empty faces from trimesh")
    trimesh.remove_empty_faces()
    print("Converting trimesh to mesh object")
    full_mesh = trimesh.trimesh_to_npmesh()
    print("Saving mesh to " + "stl/" + stlname + ".stl")
    full_mesh.save("stl/" + stlname + ".stl", mode=stl.Mode.BINARY)


# Run program
if __name__ == '__main__':
    m1 = memory_profiler.memory_usage()
    t1 = time.process_time()
    main("audio/sample.csv", "sample_engraved")
    t2 = time.process_time()
    m2 = memory_profiler.memory_usage()
    time_diff = t2 - t1
    mem_diff = m2[0] - m1[0]
    print(
        f"It took {time_diff:.2f} Secs and {mem_diff:.2f} Mb to execute this method")
