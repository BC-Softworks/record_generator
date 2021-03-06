from trimesh import TriMesh, Vertex
import pytest
import numpy as np

def test_manifold_creation():
    trimesh = TriMesh()
    assert np.array_equal(trimesh.get_faces_by_index(), np.array([]))
    assert np.array_equal(trimesh.get_vertices(), np.array([]))

def test_trimesh_add_vertices():
    trimesh = TriMesh()
    vertices = [Vertex(1, 0, 0), Vertex(0, 1, 0), Vertex(0, 0, 1)]
    trimesh.add_vertices(vertices)
    assert np.array_equal(trimesh.get_vertices(), np.array(vertices))

def test_trimesh_add_faces():
    trimesh = TriMesh()
    vertices = [Vertex(1, 0, 0), Vertex(0, 1, 0)]
    faces = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    trimesh.add_vertices(vertices)
    trimesh.add_faces_by_index(faces)
    assert np.array_equal(trimesh.get_faces_by_index(), np.array(faces))

def test_trimesh_remove_duplicate_faces():
    trimesh = TriMesh()
    vertices = [Vertex(1, 0, 0)]
    faces = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
    trimesh.add_vertices(vertices)
    trimesh.add_faces_by_index(faces)
    trimesh.remove_duplicate_faces()
    assert np.array_equal(trimesh.get_faces_by_index(), np.array([(0, 0, 0)]))

def test_trimesh_remove_empty_faces():
    trimesh = TriMesh()
    vertices = [Vertex(1, 0, 0), Vertex(0, 1, 0)]
    faces = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    trimesh.add_vertices(vertices)
    trimesh.add_faces_by_index(faces)
    trimesh.remove_empty_faces()
    assert np.array_equal(trimesh.get_faces_by_index(), np.array([]))


#Generated mesh saved to "stl/pyramidtest.stl"
import stl
def test_trimesh_pyramid_test():
    trimesh = TriMesh()
    vertices = [Vertex(1, 0, 0), Vertex(-1, 0, 0), Vertex(0, 1, 0), Vertex(0, -1, 0), Vertex(0, 0, 1)]
    faces = [(0, 2, 3), (1, 2, 3), (0, 2, 4), (1, 2, 4), (0, 3, 4), (1, 3, 4)]
    trimesh.add_vertices(vertices)
    trimesh.add_faces_by_index(faces)
    trimesh.trimesh_to_npmesh().save('stl/pyramidtest.stl', mode=stl.Mode.BINARY)
    assert np.array_equal(trimesh.get_faces_by_index(), np.array(faces))
    assert trimesh.euler_characteristic() == 3

#Generated mesh saved to "stl/cubetest.stl"
def test_trimesh_cube_test():
    trimesh = TriMesh()
    vertices = [Vertex(-1, 0, 0), Vertex(1, 0, 0), Vertex(0, 1, 0), Vertex(0, -1, 0), Vertex(1, 0, 1), Vertex(-1, 0, 1), Vertex(0, 1, 1), Vertex(0, -1, 1)]

    # Horizontial 
    trimesh.add_quad(vertices[0:4])
    trimesh.add_quad(vertices[4:])

    # Vertical
    trimesh.add_quad((vertices[0], vertices[2], vertices[5], vertices[6]))
    trimesh.add_quad((vertices[0], vertices[3], vertices[5], vertices[7]))
    trimesh.add_quad((vertices[1], vertices[3], vertices[4], vertices[7]))
    trimesh.add_quad((vertices[1], vertices[2], vertices[4], vertices[6]))

    trimesh.trimesh_to_npmesh().save('stl/cubetest.stl', mode=stl.Mode.BINARY)
    assert trimesh.euler_characteristic() == 2

def test_trimesh_merge():
    # Create squared pyramid
    pyramid_trimesh = TriMesh()
    vertices = [Vertex(1, 0, 1), Vertex(-1, 0, 1), Vertex(0, 1, 1), Vertex(0, -1, 1), Vertex(0, 0, 2)]
    faces = [(0, 2, 4), (1, 2, 4), (0, 3, 4), (1, 3, 4)]
    pyramid_trimesh.add_vertices(vertices)
    pyramid_trimesh.add_faces_by_index(faces)

    # Create cube
    cube_trimesh = TriMesh()
    vertices = [Vertex(-1, 0, 0), Vertex(1, 0, 0), Vertex(0, 1, 0), Vertex(0, -1, 0), Vertex(1, 0, 1), Vertex(-1, 0, 1), Vertex(0, 1, 1), Vertex(0, -1, 1)]

    cube_trimesh.add_quad(vertices[0:4])
    cube_trimesh.add_quad((vertices[0], vertices[2], vertices[5], vertices[6]))
    cube_trimesh.add_quad((vertices[0], vertices[3], vertices[5], vertices[7]))
    cube_trimesh.add_quad((vertices[1], vertices[3], vertices[4], vertices[7]))
    cube_trimesh.add_quad((vertices[1], vertices[2], vertices[4], vertices[6]))

    trimesh = pyramid_trimesh.merge(cube_trimesh)
    trimesh.trimesh_to_npmesh().save('stl/house_test.stl', mode=stl.Mode.BINARY)
    assert trimesh.euler_characteristic() == 5
    