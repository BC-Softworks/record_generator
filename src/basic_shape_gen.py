#!/usr/bin/python3


import os
from math import cos, sin
import time
import memory_profiler

# https://pypi.org/project/numpy-stl/
from stl import mesh

# Global variables
import record_globals as rg


def circumference_generator(theta, rad, incr=rg.incrNum):
    """Generate circumference of cylinder"""
    while theta < rg.tau:
        yield rad * sin(theta), rad * cos(theta)
        theta += incr

def polygon_generator(rad, edge_num):
    """Generate perimeter of polygon"""
    return circumference_generator(0, rad, incr=rg.tau / edge_num)


def setzpos(arr, height=0) -> tuple:
    """ Add z position to each vector of x and y """
    for lst in arr:
        yield(lst[0], lst[1], height)


def create_polygon(rad, num, height=0):
    lst = list(polygon_generator(rad, num))
    return list(setzpos(lst, height))


def add_polygon_edges(list_a, list_b, shape):
    """ tristrip edges of polygon """
    list_a.append(list_a[0])
    list_b.append(list_b[0])
    shape.tristrip(list_a, list_b)

def calculate_record_shape(
        record_shape=rg.TriMesh(),
        edge_num=20,
        info=True) -> mesh.Mesh:
    """ Combine the vectors in to an outer and inner circle """
    baseline = rg.record_height - 0.5

    outerEdgeUpper = create_polygon(rg.RADIUS, edge_num, rg.record_height)
    outerEdgeLower = create_polygon(rg.RADIUS, edge_num)

    outerSpacerUpper = create_polygon(rg.outer_rad + 0.25, edge_num, rg.record_height)
    outerSpacerMiddle = create_polygon(rg.outer_rad + 0.25, edge_num, baseline)
    outerSpacerLower = create_polygon(rg.outer_rad + 0.25, edge_num)

    innerSpacerUpper = create_polygon(rg.inner_rad, edge_num, rg.record_height)
    innerSpacerMiddle = create_polygon(rg.inner_rad, edge_num, baseline)
    innerSpacerLower = create_polygon(rg.inner_rad, edge_num)

    center_radius = rg.inner_hole / 2
    centerHoleUpper = create_polygon(center_radius, edge_num, rg.record_height)
    centerHoleMiddle = create_polygon(center_radius, edge_num, baseline)
    centerHoleLower = create_polygon(center_radius, edge_num)

    # Adding vertices to the shape
    record_shape.add_vertices(outerEdgeUpper + outerEdgeLower)
    outerSpacer = outerSpacerUpper + outerSpacerMiddle + outerSpacerLower
    record_shape.add_vertices(outerSpacer)
    innerSpacer = innerSpacerUpper + innerSpacerMiddle + innerSpacerLower
    record_shape.add_vertices(innerSpacer)
    center = centerHoleUpper + centerHoleMiddle + centerHoleLower
    record_shape.add_vertices(center)    
    if info:
        vertices = record_shape.get_vertices()
        print("Number of vertices: " + str(len(vertices)))
    
    # Draw vertical faces
    add_polygon_edges(outerEdgeUpper, outerEdgeLower, record_shape)
    add_polygon_edges(outerSpacerUpper,outerSpacerMiddle, record_shape)
    add_polygon_edges(outerSpacerMiddle,outerSpacerLower, record_shape)
    add_polygon_edges(innerSpacerUpper,innerSpacerMiddle, record_shape)
    add_polygon_edges(innerSpacerMiddle,innerSpacerLower, record_shape)
    add_polygon_edges(centerHoleUpper, centerHoleLower, record_shape)

    # Draw horizontial faces
    add_polygon_edges(outerEdgeUpper, outerSpacerUpper, record_shape)
    add_polygon_edges(innerSpacerUpper, centerHoleUpper, record_shape)
    add_polygon_edges(innerSpacerMiddle,centerHoleMiddle, record_shape)
    add_polygon_edges(outerEdgeLower, centerHoleLower, record_shape)

    if info:
        print("Number of faces: " + str(len(record_shape.get_faces())))
    return record_shape


def main() -> rg.TriMesh:
    filename = str(rg.RPM) + '_disc.stl'
    print('Generating blank record.')
    record_shape = calculate_record_shape()
    record_shape.remove_duplicate_faces()
    record_shape.remove_empty_faces()

    # Save mesh for debugging purposes
    if not os.path.isdir('stl'):
        os.mkdir('stl')
    record_mesh = record_shape.shape_to_mesh()
    print("Saving file to {}".format(filename))
    record_mesh.save("stl/" + filename)

    return record_shape


if __name__ == '__main__':
    m1 = memory_profiler.memory_usage()
    t1 = time.process_time()
    main()
    t2 = time.process_time()
    m2 = memory_profiler.memory_usage()
    time_diff = t2 - t1
    mem_diff = m2[0] - m1[0]
    print(f"It took {time_diff:.2f} Secs and {mem_diff:.2f} Mb to execute this method")
