#!/usr/bin/python3
#
#	pyglmahjong - Python OpenGL Mahjong and Shisen implementation
#	Copyright (C) 2015-2018 Johannes Bauer
#
#	This file is part of pyglmahjong.
#
#	pyglmahjong is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pyglmahjong is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pyglmahjong; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import numpy

class ObjModel(object):
	def __init__(self, filename):
		self._vertices = [ ]
		self._faces = [ ]
		self._normals = [ ]
		self._uvs = [ ]
		self._unknowncnt = 0
		self._load(filename)

	def _load(self, filename):
		for line in open(filename, "r"):
			line = line.rstrip("\r\n")
			line = line.split()
			if line[0] == "v":
				self._vertices.append(tuple(float(x) for x in line[1:]))
			elif line[0] == "vn":
				self._normals.append(tuple(float(x) for x in line[1:]))
			elif line[0] == "vt":
				uv = [ float(x) for x in line[1:] ]
				self._uvs.append(uv)
			elif line[0] == "f":
				self._faces.append([ [ int(x) for x in component.split("/") ] for component in line[1:] ])
			else:
				self._unknowncnt += 1

	def dump(self):
		bytes_per_float = 4
		floats_per_vertex = 3
		floats_per_normal = 3
		floats_per_uv = 2
		floats_per_complex_vertex = (floats_per_vertex + floats_per_normal + floats_per_uv)
		floats_per_face = floats_per_complex_vertex * 3
		bytes_per_face = bytes_per_float * floats_per_face
		bytes_per_model_naive = len(self._faces) * bytes_per_face


		bytes_per_int = 2
		ints_per_vertex_index = 3
		ints_per_normal_index = 3
		ints_per_uv_index = 2
		ints_per_complex_vertex = (ints_per_vertex_index + ints_per_normal_index + ints_per_uv_index)
		indices_per_face = ints_per_complex_vertex * 3
		index_bytes_model = len(self._faces) * indices_per_face

		storage_bytes_model = ((len(self._vertices) * floats_per_vertex) + (len(self._normals) * floats_per_normal) + (len(self._uvs) * floats_per_uv)) * bytes_per_float
		bytes_per_model_indexed = bytes_per_model_naive + storage_bytes_model

		print("Uninterpreted lines: %d" % (self._unknowncnt))
		print("%d vertices, %d vertex normals, %d UVs in %d faces" % (len(self._vertices), len(self._normals), len(self._uvs), len(self._faces)))
		print("Naive storage  : %d bytes" % (bytes_per_model_naive))
		print("Indexed storage: %d bytes (%d bytes for indices, %d bytes for storage)" % (bytes_per_model_indexed, index_bytes_model, storage_bytes_model))
		(minu, maxu, minv, maxv) = (min(u for (u, v) in self._uvs), max(u for (u, v) in self._uvs), min(v for (u, v) in self._uvs), max(v for (u, v) in self._uvs))
		print("UV min/max     : U = { %5.4f %5.4f } V = { %5.4f %5.4f }" % (minu, maxu, minv, maxv))
		width = 1024
		print("UV min/max pxl : U = { %4.0f %4.0f } V = { %4.0f %4.0f }" % (minu * width, maxu * width, minv * width, maxv * width))

		print("Object extents : %s" % (str((obj.extents()))))
		print("Object center  : %s" % (str((obj.center()))))


	def extents(self):
		return ((min(vertex[0] for vertex in self._vertices), min(vertex[1] for vertex in self._vertices), min(vertex[2] for vertex in self._vertices)),
				(max(vertex[0] for vertex in self._vertices), max(vertex[1] for vertex in self._vertices), max(vertex[2] for vertex in self._vertices)))

	def center(self):
		extents = self.extents()
		return ((extents[1][0] - extents[0][0]) / 2 + extents[0][0], (extents[1][1] - extents[0][1]) / 2 + extents[0][1], (extents[1][2] - extents[0][2]) / 2 + extents[0][2])

	def getdata(self):
		total_data = [ ]
		for face in self._faces:
			(vertex_a, uv_a, normal_a) = face[0]
			(vertex_b, uv_b, normal_b) = face[1]
			(vertex_c, uv_c, normal_c) = face[2]
			vertex_a = self._vertices[vertex_a - 1]
			vertex_b = self._vertices[vertex_b - 1]
			vertex_c = self._vertices[vertex_c - 1]
			normal_a = self._normals[normal_a - 1]
			normal_b = self._normals[normal_b - 1]
			normal_c = self._normals[normal_c - 1]
			uv_a = self._uvs[uv_a - 1]
			uv_b = self._uvs[uv_b - 1]
			uv_c = self._uvs[uv_c - 1]
			total_data += vertex_a
			total_data += normal_a
			total_data += uv_a
			total_data += vertex_b
			total_data += normal_b
			total_data += uv_b
			total_data += vertex_c
			total_data += normal_c
			total_data += uv_c

		data = numpy.array(total_data, dtype = numpy.float32)
		return data

	def savetobinfile(self, filename):
		data = self.getdata()
		print("Writing %d bytes of interlaced data to %s" % (data.nbytes, filename))
		data.tofile(filename)

if __name__ == "__main__":
	obj = ObjModel("dev/models/textured_tile.obj")
	obj.dump()
	obj.savetobinfile("data/models/piece.bin")

