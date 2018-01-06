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

from Geo3d import Vector

class Piece(object):
	WIDTH = 1.0
	HEIGHT = 0.35
	LENGTH = 1.618

	def __init__(self, x, y, z, tile = None, gridpiece = None):
		self._x = x
		self._y = y
		self._z = z
		self._globject = None
		self._tile = tile
		self._gridpiece = gridpiece
		self._state = "idle"

	def setstate(self, state):
		assert(state in [ "idle", "selected", "occluded", "occludes" ])
		self._state = state

	@property
	def globject(self):
		return self._globject

	def setglobject(self, globj):
		self._globject = globj

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
	def gridpiece(self):
		return self._gridpiece

	@property
	def dx(self):
		return self._gridpiece.dx

	@property
	def dy(self):
		return self._gridpiece.dy

	@property
	def dz(self):
		return self._gridpiece.dz

	def getcenter(self):
		return Vector(self.x, self.y, self.z)

	@property
	def length(self):
		return self.LENGTH

	@property
	def height(self):
		return self.HEIGHT

	@property
	def width(self):
		return self.WIDTH

	@property
	def tileid(self):
		return self._tile.tileid

	@property
	def face(self):
		return self._tile.face

	@property
	def state(self):
		return self._state

	def __str__(self):
		return "Piece<%s: %s>" % (self._gridpiece, self._tile)

