#!/usr/bin/env python

from math import cos, sin
import csv

# Performance mesuring
import time
import memory_profiler

# https://pypi.org/project/numpy-stl/
import stl

import record_globals as rg

from basic_shape_gen import create_polygon, calculate_record_shape


def outer_upper_vertex(rad, amp, bev, theta) -> rg.Vertex:
    width = rad + amp * bev
    return rg.Vertex(width * cos(theta), width * sin(theta), rg.record_height)


def inner_upper_vertex(rad, amp, bev, theta) -> rg.Vertex:
    width = rad - rg.groove_width - amp * bev
    return rg.Vertex(width * cos(theta), width * sin(theta), rg.record_height)


def outer_lower_vertex(rad, theta, g_h) -> rg.Vertex:
    return rg.Vertex(rad * cos(theta), rad * sin(theta), g_h)


def inner_lower_vertex(rad, theta, g_h) -> rg.Vertex:
    w = rad - rg.groove_width
    return rg.Vertex(w * cos(theta), w * sin(theta), g_h)


def groove_height(audio_array, sample_num):
    """Height of the groove extracted from the audio array"""
    baseline = rg.record_height - rg.depth - rg.amplitude
    amp = audio_array[int(rg.rate_divisor * sample_num)]
    return rg.truncate( baseline * amp, rg.precision)


def draw_groove_cap(last_edge, rad, height, shape):
    """Draws the ramp between the groove and outer cap"""
    stop1 = [outer_upper_vertex(rad, rg.amplitude, rg.bevel, 0),
             inner_upper_vertex(rad, rg.amplitude, rg.bevel, 0)]
    stop2 = [outer_lower_vertex(rad, 0, height), inner_lower_vertex(rad, 0, height)]
    shape.add_vertices(stop1 + stop2)

    # Draw triangles
    shape.tristrip(stop1, stop2)

    # Fill in around cap
    stop3 = [last_edge[-1], (rg.inner_rad, rad, rg.record_height)]
    shape.add_vertex(stop3[1])
    shape.tristrip(stop1, stop3)

    return shape


def fill_remaining_area(r, shape, edge_num=32):
    """Fill the space between the last groove and the center hole"""
    remaining_space = create_polygon(rg.inner_rad, edge_num, rg.record_height)
    edge_of_groove = create_polygon(r, edge_num, rg.record_height)
    shape.add_vertices(remaining_space + edge_of_groove)
    remaining_space.append(remaining_space[0])
    edge_of_groove.append(edge_of_groove[0])
    shape.tristrip(remaining_space, edge_of_groove)
    return shape


def draw_spiral(audio_array, rad, shape=rg.TriMesh(), info=True):
    """rad is the radial postion of the vertex beign drawn"""

    # Inner while for groove position
    last_edge = None
    index = samplenum = 0
    gH = groove_height(audio_array, samplenum)

    s1 = [outer_upper_vertex(rg.RADIUS, rg.amplitude, rg.bevel, 0),
          inner_upper_vertex(rg.RADIUS, rg.amplitude, rg.bevel, 0)]
    s2 = [outer_lower_vertex(rg.RADIUS, 0, gH), inner_lower_vertex(rg.RADIUS, 0, gH)]
    shape.add_vertices(s1 + s2)
    shape.tristrip(s1, s2)

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
        groove_vertices = groove_outer_upper + groove_outer_lower + \
            groove_inner_upper + groove_inner_lower
        shape.add_vertices(groove_vertices)

        if index == 0:
            # Draw triangle to close outer part of record
            shape.tristrip(groove_outer_upper, groove_outer_lower)
        else:
            shape.tristrip(groove_inner_upper, groove_outer_lower)

        shape.tristrip(groove_outer_lower, groove_inner_lower)
        shape.tristrip(groove_inner_lower, groove_inner_upper)
        last_edge = groove_inner_upper

        index += 1
        if info:
            print("Groove drawn: {}".format(index))

    # Draw groove cap
    gH = groove_height(audio_array, samplenum)
    shape = draw_groove_cap(last_edge, rad, gH, shape)

    # Close remaining space between last groove and center hole
    return fill_remaining_area(rad, shape)


def main(filename, stlname):

    # Read in array of bytes as float
    audio_file = open(filename, 'rt', newline='')
    lst = [x for x in csv.reader(audio_file, delimiter=',')][0]
    lst = [float(x) for x in lst if x != '']

    # Normalize the values
    current_max = max(lst)
    lst = [rg.truncate(abs(x) + current_max, rg.precision) for x in lst]
    current_max *= 4
    normalized_depth = [rg.truncate(x / current_max, rg.precision) for x in lst]

    print("Generate record shape")
    record_shape = calculate_record_shape(info=False)
    print("Drawing spiral object")
    shape = draw_spiral(normalized_depth, rg.outer_rad, record_shape)
    print("Removing duplicate faces from shape spiral object")
    shape.remove_duplicate_faces()
    print("Removing empty faces from shape spiral object")
    shape.remove_empty_faces()
    print("Converting shape to mesh object")
    full_mesh = shape.shape_to_mesh()
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
