#!/usr/bin/python3


import os
from math import cos, sin
import time
import memory_profiler

# https://pypi.org/project/numpy-stl/
from stl import mesh

import trimesh as tm
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
        yield tm.Vertex(lst[0], lst[1], height)


def create_polygon(rad, num, height=0):
    vertex_list = list(polygon_generator(rad, num))
    lst = list(setzpos(vertex_list, height))[0:num+1]
    lst.append(lst[0])
    assert len(lst) == num + 1
    return lst

def calculate_record_shape(
        trimesh=tm.TriMesh(),
        edge_num=32,
        info=True) -> mesh.Mesh:
    """ Combine the vectors in to an outer and inner circle """
    baseline = rg.record_height - 1.75

    outerEdgeUpper = create_polygon(rg.RADIUS, edge_num, rg.record_height)
    outerEdgeLower = create_polygon(rg.RADIUS, edge_num)

    outerSpacerUpper = create_polygon(rg.outer_rad + 0.5, edge_num, rg.record_height)
    outerSpacerMiddle = create_polygon(rg.outer_rad + 0.5, edge_num, baseline)

    innerSpacerUpper = create_polygon(rg.inner_rad, edge_num, rg.record_height)
    innerSpacerMiddle = create_polygon(rg.inner_rad, edge_num, baseline)

    center_radius = rg.inner_hole / 2
    centerHoleUpper = create_polygon(center_radius, edge_num, rg.record_height)
    centerHoleLower = create_polygon(center_radius, edge_num)
    
    # Draw vertical faces
    trimesh.quadstrip(outerEdgeUpper, outerEdgeLower)
    trimesh.quadstrip(outerSpacerUpper, outerSpacerMiddle)
    trimesh.quadstrip(innerSpacerUpper, innerSpacerMiddle)
    trimesh.quadstrip(centerHoleUpper, centerHoleLower)

    # Draw horizontial faces
    trimesh.tristrip(outerEdgeUpper, outerSpacerUpper)
    trimesh.tristrip(outerSpacerMiddle, innerSpacerMiddle)
    trimesh.tristrip(innerSpacerUpper, centerHoleUpper)
    trimesh.tristrip(outerEdgeLower, centerHoleLower)

    if info:
        vertices = trimesh.get_vertices()
        print("Number of vertices: " + str(len(vertices)))
        print("Number of faces: " + str(len(trimesh)))
        print("Number of edges: " + str(len(trimesh.get_edges())))
    return trimesh


def main():
    filename = str(rg.RPM) + '_disc.stl'
    print('Generating blank record.')
    record_trimesh = calculate_record_shape()
    record_trimesh.remove_duplicate_faces()
    record_trimesh.remove_empty_faces()

    # Save mesh for debugging purposes
    if not os.path.isdir('stl'):
        os.mkdir('stl')
    record_mesh = record_trimesh.trimesh_to_npmesh()
    print("Saving file to {}".format(filename))
    record_mesh.save("stl/" + filename)

if __name__ == '__main__':
    m1 = memory_profiler.memory_usage()
    t1 = time.process_time()
    main()
    t2 = time.process_time()
    m2 = memory_profiler.memory_usage()
    time_diff = t2 - t1
    mem_diff = m2[0] - m1[0]
    print(f"It took {time_diff:.2f} Secs and {mem_diff:.2f} Mb to execute this method")
