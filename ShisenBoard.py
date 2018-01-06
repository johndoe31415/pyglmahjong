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

import itertools
import collections
import random

from Backtracking import BacktrackingSolvable, BacktrackingSolver
from ShisenPath import ShisenConnection
from AbstractBoard import AbstractBoard

class ShisenBoard(AbstractBoard, BacktrackingSolvable):
	def __init__(self):
		AbstractBoard.__init__(self)
		BacktrackingSolvable.__init__(self)
		self._piecedict = { }
		self._minx = 0
		self._maxx = 0
		self._miny = 0
		self._maxy = 0

	def _calc_minmax(self):
		if self.piececnt == 0:
			self._minx = 0
			self._maxx = 0
			self._miny = 0
			self._maxy = 0
		else:
			self._minx = min(key[0] for key in self._piecedict.keys())
			self._miny = min(key[1] for key in self._piecedict.keys())
			self._maxx = max(key[0] for key in self._piecedict.keys())
			self._maxy = max(key[1] for key in self._piecedict.keys())

	def _calc_minmax_conditionally(self, piece):
		if (piece.dx <= self._minx) or (piece.dx >= self._maxx) or (piece.dz <= self._miny) or (piece.dz >= self._maxy):
			self._calc_minmax()

	@property
	def piececnt(self):
		return len(self._piecedict)

	def backtrack_clone(self):
		clone = ShisenBoard()
		clone._piecedict = dict(self._piecedict)
		return clone

	def backtrack_condition_satisfied(self):
		return self.piececnt == 0

	def backtrack_choices(self):
		yield from self.possible_moves()

	def backtrack_makechoice(self, choice):
		(piece1, piece2) = choice
		self.remove_piece(piece1)
		self.remove_piece(piece2)

	def backtrack_reversechoice(self, choice):
		(piece1, piece2) = choice
		self.add_piece(piece1)
		self.add_piece(piece2)

	def clear(self):
		self._piecedict = { }

	def getpiece(self, dx, dy):
		return self._piecedict.get((dx, dy))

	def add_piece(self, piece):
		assert(self.getpiece(piece.dx, piece.dz) is None)
		self._piecedict[(piece.dx, piece.dz)] = piece
		self._calc_minmax_conditionally(piece)

	def remove_piece(self, *pieces):
		for piece in pieces:
			assert(self.getpiece(piece.dx, piece.dz) is not None)
			del self._piecedict[(piece.dx, piece.dz)]
			self._calc_minmax_conditionally(piece)

	def solve(self):
		return BacktrackingSolver(self).solve()

	def iterpieces(self):
		return iter(self._piecedict.values())

	def possible_moves(self):
		piece_by_tileid = collections.defaultdict(list)
		for piece in self.iterpieces():
			piece_by_tileid[piece.tileid].append(piece)

		for similar_pieces in piece_by_tileid.values():
			for (piece1, piece2) in itertools.combinations(similar_pieces, 2):
				if self.valid_move(piece1, piece2):
					yield (piece1, piece2)

	def possible_movecnt(self):
		return len(list(self.possible_moves()))

	def valid_move(self, piece1, piece2):
		if piece1.tileid != piece2.tileid:
			return None

		# Construct paths
		conn = ShisenConnection(piece1.dx, piece1.dz, piece2.dx, piece2.dz, self._minx, self._miny, self._maxx, self._maxy)
		for path in conn.paths():
			for (x, y) in path.walk():
				if self.getpiece(x, y) is not None:
					break
			else:
				return path.getpoints()

		return None

	def piece_selectable(self, piece):
		return True

	def get_occlusions(self, piece):
		return set()

	def random_pair(self):
		while True:
			(pc1, pc2) = random.sample(list(self._piecedict.values()), 2)
			if self.valid_move(pc1, pc2):
				return [ pc1, pc2 ]


	def boardlayout_random_pairs(self):
		self = self.backtrack_clone()
		while self.piececnt > 0:
			move = random.sample(list(self._piecedict.values()), 2)
			yield move
			self.remove_piece(move[0], move[1])

