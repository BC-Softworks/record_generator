
import copy
from collections import OrderedDict, namedtuple

from math import sqrt

import numpy as np
from bidict import bidict
# https://pypi.org/project/numpy-stl/
from stl import mesh

from skiplist import SkipList

Vertex = namedtuple('Vertex', 'x y z')

def vector_length(face):
    """Length of each vector in a triangle"""
    def length(v1, v2):
        x2 = v2.x - v1.x
        y2 = v2.y - v1.y
        z2 = v2.z - v1.z
        return sqrt(x2 + y2 + z2)

    return length(face[0], face[1]), length(face[0], face[2]), length(face[1], face[2])

def area_of_triangle(abc):
    """Heron's formula for the area of a triangle"""
    a, b, c = abc
    a_squared = a ** 2
    c_squared = c ** 2
    return sqrt(abs(a_squared  * c_squared - ((a_squared + c_squared - (b ** 2)) / 2) ** 2)) / 2
    
class TriMesh():
    def __init__(self, dictionary={}):
        self.vertices = bidict(dictionary)
        self.faces = SkipList(less_than = lambda a, b : area_of_triangle(a) <  area_of_triangle(b))

    def __str__(self):
        return str(self.vertices)

    def __len__(self):
        return len(self.faces)

    def add_vertex(self, xyz) -> int:
        assert len(xyz) == 3
        index = len(self.vertices)
        if xyz not in self.vertices.inverse:
            self.vertices[index] = Vertex(*xyz)
            return index
        else:
            return -1

    def add_vertices(self, lst):
        for v in lst:
            self.add_vertex(Vertex(*v))

    # It is faster to add all the faces and remove duplicates at the end
    # then to check after every add
    def add_face(self, vertices):
        self.add_vertices(vertices)
        new_face = tuple([self.vertices.inverse[item] for item in vertices])
        # Ordering the faces by size to speed up searches
        self.faces.insert(new_face)

    def get_vertices(self):
        """ Returns a numpy array of cartesian coordinates """
        lst = [self.vertices[i] for i in range(0, len(self.vertices))]
        return np.array(lst)

    def get_faces_vertices(self):
        for f in self.faces.to_generator():
            yield tuple(map(lambda index: self.vertices[index], f))

    def get_faces_by_index(self):
        return np.array(self.faces.to_list())

    def tristrip(self, list_a, list_b):
        lst = min(len(list_a), len(list_b)) - 1
        for i in range(0, lst):
            self.add_face(Vertex(list_a[i], list_a[i + 1], list_b[i]))
            self.add_face(Vertex(list_b[i], list_b[i + 1], list_a[i + 1]))

    def merge(self, trimesh):
        assert isinstance(trimesh, self)
        self.add_vertices(trimesh.get_vertices().tolist())
        for face in trimesh.get_faces_vertices():
            self.add_face(face)

    def remove_empty_faces(self, info=False):
        """ Removes faces of colinear vertices"""
        number_of_faces = len(self)
        for f in self.faces.to_generator():
            if f[0] != f[1] and f[0] != f[2]:
                self.faces.remove(f)

        if info:
            print("Faces removed: ", number_of_faces - len(self))

    def remove_interior_faces(self, tiny = 0.05, info=False):
        """ Remove small faces that are overlapped completly by a large face """
        
        def tiny_faces():
            for f in self.faces:
                area = area_of_triangle(vector_lengths(f))
                if area > tiny:
                    yield face
        
        number_of_faces = len(self)
        # TODO: Add loop to check if small faces need removed
        if info:
            print("Faces removed: ", number_of_faces - len(self))

    def trimesh_to_npmesh(self) -> mesh.Mesh:
        vertices = self.get_vertices()
        number_of_faces = len(self.faces)
        faces = self.faces.to_list()
        rec = mesh.Mesh(
            data=np.zeros(number_of_faces, dtype=mesh.Mesh.dtype), speedups=True)
        for f in range(number_of_faces):
            for j in range(3):
                rec.vectors[f][j] = vertices[faces[f][j], :]
        return rec
