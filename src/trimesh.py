
import copy
from collections import OrderedDict, namedtuple
from math import sqrt
from itertools import combinations

import numpy as np
from bidict import bidict
# https://pypi.org/project/numpy-stl/
from stl import mesh

Vertex = namedtuple('Vertex', 'x y z')

def squared_magnitude(a, b):
    return (b.x - a.x) ** 2 + (b.y - a.y) ** 2 + (b.z - a.z) ** 2

def magnitude(a, b):
    return sqrt(squared_magnitude(a, b))


def midpoint(a, b):
    return Vertex((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2)


def area_of_triangle(vertices):
    """Faster triangle area calculator"""
    a, b, c = vertices

    base = magnitude(a, b)
    height = magnitude(midpoint(a, b), c)
    return base * height / 2


class TriMesh():
    def __init__(self, dictionary={}):
        self.vertices = bidict(dictionary)
        self.faces = []

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
        self.faces.append(new_face)

    def add_faces(self, lst):
        for f in lst:
            self.add_face(Vertex(*f))

    def add_faces_by_index(self, lst):
        for f in lst:
            if max(f) < len(self.vertices):
                self.faces.append(f)
            else:
                raise IndexError

    def add_quad(self, faces):
        """Add quaderlateral face"""
        assert len(faces) == 4
        def draw_triangles(diagonal_1, diagonal_2):
            a, d = diagonal_1
            b, c = diagonal_2
            self.add_face([a, b, c])
            self.add_face([b, c, d])
        
        dist = [0]
        for i in range(1,4):
            dist.append(squared_magnitude(faces[0], faces[i]))
        index = dist.index(max(dist))
        if index == 1:
            draw_triangles((faces[0], faces[1]), (faces[2], faces[3]))
        elif index == 2:
            draw_triangles((faces[0], faces[2]), (faces[1], faces[3]))
        else:
            draw_triangles((faces[0], faces[3]), (faces[1], faces[2]))

    def get_vertices(self):
        """ Returns a numpy array of cartesian coordinates """
        lst = [self.vertices[i] for i in range(0, len(self.vertices))]
        return np.array(lst)

    def get_faces_vertices(self):
        for f in self.faces:
            yield tuple(map(lambda index: self.vertices[index], f))

    def get_faces_by_index(self):
        return np.array(self.faces)

    def get_edges(self):
        edge_lst = []
        for face in self.faces:
            edge_lst.extend(combinations(list(face), 2))
        return set(edge_lst)

    def tristrip(self, list_a, list_b):
        lst = min(len(list_a), len(list_b)) - 1
        for i in range(0, lst):
            self.add_face(Vertex(list_a[i], list_a[i + 1], list_b[i]))
            self.add_face(Vertex(list_b[i], list_b[i + 1], list_a[i + 1]))
        
    def quadstrip(self, list_a, list_b):
        lst = min(len(list_a), len(list_b)) - 1
        for i in range(0, lst):
            self.add_quad((list_a[i], list_a[i + 1], list_b[i], list_b[i+1]))
            

    def merge(self, trimesh):
        assert type(self) == type(trimesh)
        self.add_vertices(trimesh.get_vertices().tolist())
        for face in trimesh.get_faces_vertices():
            self.add_face(face)
        return self

    def _faces_removed(self, func, string = ''):
        number_of_faces = len(self)
        self.faces = func(self.faces)
        print(string + "Faces removed: ", number_of_faces - len(self))

    def remove_duplicate_faces(self):
        self._faces_removed(lambda x: list(OrderedDict.fromkeys(x)), 'Duplicate ')

    def remove_empty_faces(self):
        """ Removes faces of colinear vertices"""
        self._faces_removed(lambda x: list(
            filter(lambda f: f[0] != f[1] and f[0] != f[2] and f[1] != f[2], x)), 'Empty ')

    def euler_characteristic(self):
        number_of_vertices = len(self.faces)
        number_of_faces = len(self.faces)
        edge_set = self.get_edges()
        number_of_edges = len(edge_set)
        return abs(number_of_vertices - number_of_edges + number_of_faces)

    def trimesh_to_npmesh(self) -> mesh.Mesh:
        vertices = self.get_vertices()
        number_of_faces = len(self.faces)
        faces = self.faces
        rec = mesh.Mesh(
            data=np.zeros(number_of_faces, dtype=mesh.Mesh.dtype), speedups=True)
        for f in range(number_of_faces):
            for j in range(3):
                rec.vectors[f][j] = vertices[faces[f][j], :]
        return rec
