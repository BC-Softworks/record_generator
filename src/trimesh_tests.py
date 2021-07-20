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

#Generated mesh saved to "stl/pyramidtest.stl"
import stl
def test_trimesh_is_manifold():
    trimesh = TriMesh()
    vertices = [Vertex(1, 0, 0), Vertex(-1, 0, 0), Vertex(0, 1, 0), Vertex(0, -1, 0), Vertex(0, 0, 1)]
    faces = [(0, 1, 2), (0, 2, 3), (0, 1, 4), (1, 2, 4), (2, 3, 4), (0, 3, 4)]
    trimesh.add_vertices(vertices)
    trimesh.add_faces_by_index(faces)
    trimesh.trimesh_to_npmesh().save('stl/pyramidtest.stl', mode=stl.Mode.BINARY)
    assert np.array_equal(trimesh.get_faces_by_index(), np.array(faces))
    assert trimesh.is_manifold()
