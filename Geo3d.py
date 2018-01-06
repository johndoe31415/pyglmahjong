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

import math
import numpy

# Model:		Model coordinates -> World coordinates
# View:			World coordinates -> Camera coordinates
# Projection:	Camera -> Screen

class Matrix4(object):
	"""Uses row vectors. I.e.

	Matrix4([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])

	corresponds to the matrix
	1  2  3  4
	5  6  7  8
	9  10 11 12
	13 14 15 16
	"""

	def __init__(self, matrix = None):
		if matrix is None:
			self._matrix = numpy.zeros((4, 4), dtype = numpy.float32)
		elif isinstance(matrix, list) or isinstance(matrix, tuple):
			self._matrix = numpy.array(matrix, dtype = numpy.float32)
		else:
			self._matrix = matrix

	def parse(source):
		source = [ [ float(value) for value in line.split() ] for line in source.split("\n") ]
		return Matrix4(source)

	def unproject(screencoords, viewmatrix, projmatrix, viewport):
		inverse = (projmatrix * viewmatrix).invert()

		window_vect = list(screencoords) + [ 1 ]
		window_vect[0] = (window_vect[0] - viewport[0]) / viewport[2]
		window_vect[1] = (window_vect[1] - viewport[1]) / viewport[3]
		window_vect = [ (element * 2) - 1 for element in window_vect ]

		obj_vect = inverse.mv(window_vect)
		obj_vect = [ (element / obj_vect[3]) for element in obj_vect ]
		obj_vect = Vector(*obj_vect[:3])
		return obj_vect

	def __mul__(self, other):
		result = numpy.matrix(self._matrix) * numpy.matrix(other._matrix)
		return Matrix4(numpy.asarray(result))

	def togl(self):
		return numpy.asarray(numpy.matrix(self._matrix).T).flatten()

	def str_mpl(self):
		m = [ ]
		for i in range(4):
			m.append([ ])
			for j in range(4):
				m[-1].append(self._matrix[i][j])
		return "%s" % (str(m))

	def dump_wa(self):
		m = [ ]
		for i in range(4):
			m.append([ ])
			for j in range(4):
				m[-1].append(self._matrix[i][j])
		print("%s" % (str(m).replace("[", "{").replace("]", "}")))

	def str_glm(self):
		lines = [ ]
		for i in range(4):
			line = [ ]
			for j in range(4):
				line.append("%.5ff" % (self._matrix[j][i]))
			lines.append("glm::vec4(%s)" % (", ".join(line)))

		return "glm::mat4(%s);" % (", ".join(lines))

	def identity():
		matrix = Matrix4()
		for i in range(4):
			matrix._matrix[i][i] = 1
		return matrix

	# Perspective Matrix
	def perspective(fovy, aspect, near, far):
		matrix = Matrix4()
		tanHalfFovy = math.tan(fovy / 2)
		matrix[(0, 0)] = 1 / (aspect * tanHalfFovy)
		matrix[(1, 1)] = 1 / tanHalfFovy
		matrix[(2, 2)] = -(far + near) / (far - near)
		matrix[(3, 2)] = -1
		matrix[(2, 3)] = -(2 * far * near) / (far - near)
		return matrix

	# View Matrix
	def lookat(eye, center, up):
		matrix = Matrix4()
		f = (center - eye).normalize()
		s = f.crossprod(up).normalize()
		u = s.crossprod(f)
		matrix[(3, 3)] = 1
		matrix[(0, 0)] = s.x
		matrix[(0, 1)] = s.y
		matrix[(0, 2)] = s.z
		matrix[(1, 0)] = u.x
		matrix[(1, 1)] = u.y
		matrix[(1, 2)] = u.z
		matrix[(2, 0)] = -f.x
		matrix[(2, 1)] = -f.y
		matrix[(2, 2)] = -f.z
		matrix[(0, 3)] = -s.dotprod(eye)
		matrix[(1, 3)] = -u.dotprod(eye)
		matrix[(2, 3)] = f.dotprod(eye)
		return matrix

	def clone(self):
		return Matrix4(numpy.array(self._matrix))

	def translate(self, v):
		clone = self.clone()
		clone._setcol(3, (self._getcol(0) * v.x) + (self._getcol(1) * v.y) + (self._getcol(2) * v.z) + self._getcol(3))
		return clone

	def _setcol(self, col, values):
		for (i, value) in enumerate(values):
			self._matrix[i][col] = value

	def _getcol(self, col):
		return self._matrix.flatten()[col : : 4]

	def transpose(self):
		return Matrix4(numpy.asarray(numpy.matrix(self._matrix).T))

	def rotate(self, angle, axis):
		c = math.cos(angle)
		s = math.sin(angle)
		axis = axis.normalize()
		temp = (1 - c) * axis

		rotate = Matrix4()
		rotate[(0, 0)] = c + temp.x * axis.x
		rotate[(0, 1)] = 0 + temp.x * axis.y + s * axis.z
		rotate[(0, 2)] = 0 + temp.x * axis.z - s * axis.y

		rotate[(1, 0)] = 0 + temp.y * axis.x - s * axis.z
		rotate[(1, 1)] = c + temp.y * axis.y
		rotate[(1, 2)] = 0 + temp.y * axis.z + s * axis.x

		rotate[(2, 0)] = 0 + temp.z * axis.x + s * axis.y
		rotate[(2, 1)] = 0 + temp.z * axis.y - s * axis.x
		rotate[(2, 2)] = c + temp.z * axis.z

		rotated = numpy.empty((4, 4), dtype = numpy.float32)
		rotated[0] = self._getcol(0) * rotate[(0, 0)] + self._getcol(1) * rotate[(0, 1)] + self._getcol(2) * rotate[(0, 2)]
		rotated[1] = self._getcol(0) * rotate[(1, 0)] + self._getcol(1) * rotate[(1, 1)] + self._getcol(2) * rotate[(1, 2)]
		rotated[2] = self._getcol(0) * rotate[(2, 0)] + self._getcol(1) * rotate[(2, 1)] + self._getcol(2) * rotate[(2, 2)]
		rotated[3] = self._getcol(3)
		return Matrix4(numpy.asarray(numpy.matrix(rotated).T))

	def mv(self, vector):
		M = numpy.matrix(self._matrix)
		result = numpy.asarray(M.dot(vector))[0]
		return result

	def invert(self):
		inverse = numpy.linalg.inv(numpy.matrix(self._matrix))
		return Matrix4(numpy.asarray(inverse))

	def __setitem__(self, loc, value):
		self._matrix[loc[0]][loc[1]] = value

	def __getitem__(self, loc):
		return self._matrix[loc[0]][loc[1]]

	def dump(self):
		for y in range(4):
			print("[ " + "  " .join("%7.4f" % (value) for value in self._matrix[y]) + " ]")
		print()

	def __str__(self):
		return "Matrix<4x4>"

class Vector(object):
	def __init__(self, x, y, z):
		self._x = float(x)
		self._y = float(y)
		self._z = float(z)

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y

	@property
	def z(self):
		return self._z

	def rotZ(self, phi):
		return Vector(self.x * math.cos(phi) - self.y * math.sin(phi), self.x * math.sin(phi) + self.y * math.cos(phi), self.z)

	def rotY(self, phi):
		return Vector(self.x * math.cos(phi) + self.z * math.sin(phi), self.y, -self.x * math.sin(phi) + self.z * math.cos(phi))

	def rotX(self, phi):
		return Vector(self.x, self.y * math.cos(phi) - self.z * math.sin(phi), self.y * math.sin(phi) + self.z * math.cos(phi))

	def normalize(self):
		return self / self.length()

	def length(self):
		return math.sqrt((self.x ** 2) + (self.y ** 2) + (self.z ** 2))

	def crossprod(self, other):
		return Vector(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)

	def scalarprod(self, other):
		return self.x * other.x + self.y * other.y + self.z * other.z
	dotprod = scalarprod

	def same_direction(self, other):
		return (self.normalize() - other.normalize()).length() < 1e-6

	def normal(self, other):
		return self.crossprod(other).normalize()

	def inclination(self, other):
		return math.atan2(self.crossprod(other).length(), self.scalarprod(other))

	def affect(self, transformations, *values):
		for (transformation, value) in zip(transformations, values):
			if transformation == "x":
				self = Vector(self.x + value, self.y, self.z)
			elif transformation == "y":
				self = Vector(self.x, self.y + value, self.z)
			elif transformation == "z":
				self = Vector(self.x, self.y, self.z + value)
			else:
				raise Exception("Unknown transformation '%s'" % (transformation))
		return self

	def setlength(self, length):
		return self * (length / self.length())

	def __iter__(self):
		return iter((self.x, self.y, self.z))

	def __rmul__(self, other):
		return self * other

	def __mul__(self, scalar):
		return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

	def __neg__(self):
		return Vector(-self.x, -self.y, -self.z)

	def __truediv__(self, scalar):
		return self * (1 / scalar)

	def __add__(self, other):
		return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other):
		return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

	def __str__(self):
		return "(%.3f, %.3f, %.3f)" % (self.x, self.y, self.z)


class Line(object):
	"""x = a + lambda * u"""
	def __init__(self, a, u):
		assert(isinstance(a, Vector))
		assert(isinstance(u, Vector))
		self._a = a
		self._u = u.normalize()

	@property
	def a(self):
		return self._a

	@property
	def u(self):
		return self._u

	def perpendicular(self, z):
		return self._a + (((z - self._a).scalarprod(self._u)) / (self._u.scalarprod(self._u))) * self._u

	def inclination(self, axis):
		return self._u.inclination(axis)

	@property
	def angleX(self):
		return self.inclination(Vector(1, 0, 0))

	@property
	def angleY(self):
		return self.inclination(Vector(0, 1, 0))

	@property
	def angleZ(self):
		return self.inclination(Vector(0, 0, 1))

	def angle_to_quaternion(self):
		return Quaternion.from_euler_angles(self.angleX, self.angleY, self.angleZ)

	def through(x, y):
		assert(isinstance(x, Vector))
		assert(isinstance(y, Vector))
		return Line(x, y - x)

	def point(self, lambdaval):
		return self._a + lambdaval * self._u

	def __str__(self):
		return "x = %s + %s * lambda (Incl %.1f°, %.1f°, %.1f°)" % (self.a, self.u, self.angleX * 180 / math.pi, self.angleY * 180 / math.pi, self.angleZ * 180 / math.pi)

class Plane(object):
	"""x = a + lambda * u + mu * v"""
	def __init__(self, a, u, v):
		assert(isinstance(a, Vector))
		assert(isinstance(u, Vector))
		assert(isinstance(v, Vector))
		self._a = a
		self._u = u.normalize()
		self._v = v.normalize()

	@property
	def a(self):
		return self._a

	@property
	def u(self):
		return self._u

	@property
	def v(self):
		return self._v

	def normal(self):
		return self.u.crossprod(self.v).normalize()

	def through(x, y, z):
		assert(isinstance(x, Vector))
		assert(isinstance(y, Vector))
		assert(isinstance(z, Vector))
		return Plane(x, y - x, z - x)

	def __str__(self):
		return "x = %s + %s * lambda + %s * mu" % (self.a, self.u, self.v)

class Quaternion(object):
	def __init__(self, x, y, z, w):
		self._x = x
		self._y = y
		self._z = z
		self._w = w

	def from_axis_angle(axis, angle):
		assert(isinstance(axis, Vector))
		axis = axis.normalize()
		x = axis.x * math.sin(angle / 2)
		y = axis.y * math.sin(angle / 2)
		z = axis.z * math.sin(angle / 2)
		w = math.cos(angle / 2)
		return Quaternion(x, y, z, w)

	def from_euler_angles(pitch, yaw, roll):
		p = pitch  / 2
		y = yaw / 2
		r = roll / 2

		sinp = math.sin(p)
		siny = math.sin(y)
		sinr = math.sin(r)
		cosp = math.cos(p)
		cosy = math.cos(y)
		cosr = math.cos(r)

		result = Quaternion(
			sinr * cosp * cosy - cosr * sinp * siny,
			cosr * sinp * cosy + sinr * cosp * siny,
			cosr * cosp * siny - sinr * sinp * cosy,
			cosr * cosp * cosy + sinr * sinp * siny
		)
		result = result.normalize()
		return result

	def from_src_dst(src, dst):
		axis = src.normalize() + dst.normalize()
		if axis.length() < 1e-6:
			return Quaternion(1, 0, 0, 0)	# Identity
		else:
			return Quaternion.from_axis_angle(axis, math.pi)

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y

	@property
	def z(self):
		return self._z

	@property
	def w(self):
		return self._w

	def normalize(self):
		mag = self.mag()
		return Quaternion(self.x / mag, self.y / mag, self.z / mag, self.w / mag)

	def rotate(self, vector):
		vector = vector.normalize()
		vecquat = Quaternion(vector.x, vector.y, vector.z, 0)
		result = self * vecquat * self.complconj()
		return Vector(result.x, result.y, result.z)

	def __mul__(self, other):
		return Quaternion(
				self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
				self.w * other.y + self.y * other.w + self.z * other.x - self.x * other.z,
				self.w * other.z + self.z * other.w + self.x * other.y - self.y * other.x,
				self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
		)

	def getmatrix(self):
		x = Vector(1, 0, 0)
		y = Vector(0, 1, 0)
		z = Vector(0, 0, 1)

		x_t = self.rotate(x)
		y_t = self.rotate(y)
		z_t = self.rotate(z)

		return [
			[ x.dotprod(x_t), y.dotprod(x_t), z.dotprod(x_t), 0 ],
			[ x.dotprod(y_t), y.dotprod(y_t), z.dotprod(y_t), 0 ],
			[ x.dotprod(z_t), y.dotprod(z_t), z.dotprod(z_t), 0 ],
			[ 0, 0, 0, 1 ]
		]

#	def getmatrix(self):
#		x2 = self.x * self.x
#		y2 = self.y * self.z
#		z2 = self.y * self.z
#		xy = self.x * self.y
#		xz = self.x * self.z
#		yz = self.y * self.z
#		wx = self.w * self.x
#		wy = self.w * self.y
#		wz = self.w * self.z
#
#		return [
#				[ 1 - 2 * (y2 + z2),	2 * (xy - wz),		2 * (xz + wy),		0 ],
#				[ xy + wz,				1 - (x2 + z2),		yz - wx, 			0 ],
#				[ xz - wy,				yz + wx,			1 - (x2 + y2),		0 ],
#				[ 0,					0,					0,					1 ]
#		]

	def mag(self):
		return math.sqrt((self.x ** 2) + (self.y ** 2) + (self.z ** 2) + (self.w ** 2))

	def complconj(self):
		return Quaternion(-self.x, -self.y, -self.z, self.w)

	def __str__(self):
		return "Quat<%.3f, %.3f, %.3f, %.3f>" % (self.x, self.y, self.z, self.w)

if __name__ == "__main__":
	pass



