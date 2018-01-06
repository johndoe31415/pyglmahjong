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

import collections

from XMLParser import XMLParser

GridPiece = collections.namedtuple("GridPiece", [ "dx", "dy", "dz" ])

class Layout(object):
	def __init__(self, filename):
		xml = XMLParser().parsefile(filename)
		self._name = xml["name"]
		self._gridlen = int(xml["grid"])
		self._pieces = [ ]
		for piece in xml.piece:
			(x, y, z) = (int(piece["x"]), int(piece["y"]), int(piece["z"]))
			if (x < 0) or (y < 0) or (z < 0):
				raise Exception("Coordinates in layout (%d, %d, %d) are smaller than zero." % (x, y, z))
			self._pieces.append(GridPiece(dx = x, dy = y, dz = z))
		self._pieces.sort(key = lambda tile: (tile.dx, tile.dz, tile.dy))

	@property
	def name(self):
		return self._name

	@property
	def gridlen(self):
		return self._gridlen

	@property
	def grid(self):
		return 1 / self._gridlen

	def center(self):
		maxdx = (max(piece.dx for piece in self._pieces) * self.grid) + 1
		maxdy = (max(piece.dy for piece in self._pieces) * self.grid) + 1
		maxdz = (max(piece.dz for piece in self._pieces) * self.grid) + 1
		return (maxdx / 2, maxdy / 2, maxdz / 2)

	def iterpieces(self):
		return iter(self._pieces)

	def __len__(self):
		return len(self._pieces)

	def __str__(self):
		return "Layout<%s, %d pcs>" % (self.name, len(self))
