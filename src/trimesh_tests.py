from record_globals import TriMesh, Vertex
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