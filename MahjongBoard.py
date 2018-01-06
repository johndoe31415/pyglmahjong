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
import copy

from AbstractBoard import AbstractBoard
from Backtracking import BacktrackingSolvable, BacktrackingSolver

class MahjongBoard(AbstractBoard, BacktrackingSolvable):
	def __init__(self, gridlen):
		AbstractBoard.__init__(self)
		BacktrackingSolvable.__init__(self)
		self._piecedict = collections.defaultdict(lambda: collections.defaultdict(dict))
		self._piececnt = 0
		self._gridlen = gridlen

	@property
	def piececnt(self):
		return self._piececnt

	def backtrack_clone(self):
		clone = MahjongBoard(self._gridlen)
		clone._piececnt = self._piececnt
		clone._piecedict = copy.deepcopy(self._piecedict)
		return clone

	def backtrack_condition_satisfied(self):
		return self._piececnt == 0

	def backtrack_choices(self):
		yield from self.possible_moves()

	def backtrack_makechoice(self, choice):
		(piece1, piece2) = choice
		self.remove_piece(piece1, piece2)

	def backtrack_reversechoice(self, choice):
		(piece1, piece2) = choice
		self.add_piece(piece1)
		self.add_piece(piece2)

	def clear(self):
		self._piececnt = 0
		self._piecedict = collections.defaultdict(lambda: collections.defaultdict(dict))

	def getpiece(self, dx, dy, dz):
		return self._piecedict[dx][dz].get(dy)

	def add_piece(self, piece):
		assert(self.getpiece(piece.dx, piece.dy, piece.dz) is None)
		self._piecedict[piece.dx][piece.dz][piece.dy] = piece
		self._piececnt += 1

	def remove_piece(self, *pieces):
		for piece in pieces:
			assert(self.getpiece(piece.dx, piece.dy, piece.dz) is not None)
			self._piececnt -= 1
			del self._piecedict[piece.dx][piece.dz][piece.dy]

	def piece_occluded(self, piece):
		# Check if any tile on top
		for xoffset in range(-self._gridlen + 1, self._gridlen):
			for zoffset in range(-self._gridlen + 1, self._gridlen):
				candidate = self.getpiece(piece.dx + xoffset, piece.dy + 1, piece.dz + zoffset)
				if candidate is not None:
					return True

		# Check if any tile left and right
		tile_left = False
		tile_right = False
		for zoffset in range(-self._gridlen + 1, self._gridlen):
			tile_left = tile_left or self.getpiece(piece.dx - self._gridlen, piece.dy, piece.dz + zoffset)
			tile_right = tile_right or self.getpiece(piece.dx + self._gridlen, piece.dy, piece.dz + zoffset)
		return (tile_left and tile_right)

	def piece_selectable(self, piece):
		return not self.piece_occluded(piece)

	def get_occlusions(self, piece):
		occlusions = set()

		# Check if any tile on top
		for xoffset in range(-self._gridlen + 1, self._gridlen):
			for zoffset in range(-self._gridlen + 1, self._gridlen):
				candidate = self.getpiece(piece.dx + xoffset, piece.dy + 1, piece.dz + zoffset)
				if candidate is not None:
					occlusions.add(("top", candidate))

		# Check if any tile left and right
		occl_left = set()
		occl_right = set()
		for zoffset in range(-self._gridlen + 1, self._gridlen):
			candidate = self.getpiece(piece.dx - self._gridlen, piece.dy, piece.dz + zoffset)
			if candidate is not None:
				occl_left.add(("left", candidate))

			candidate = self.getpiece(piece.dx + self._gridlen, piece.dy, piece.dz + zoffset)
			if candidate is not None:
				occl_right.add(("right", candidate))

		if (len(occl_left) > 0) and (len(occl_right) > 0):
			occlusions |= occl_left
			occlusions |= occl_right
		return occlusions

	def possible_moves(self):
		possible = 0

		pieces_by_tileid = collections.defaultdict(list)
		for piece in self.iterpieces():
			pieces_by_tileid[piece.tileid].append(piece)

		for identical_pieces in pieces_by_tileid.values():
			non_occluded = [ piece for piece in identical_pieces if not self.piece_occluded(piece) ]
			for (piece1, piece2) in itertools.combinations(non_occluded, 2):
				yield (piece1, piece2)

	def nonoccludedpieces(self):
		return [ piece for piece in self.iterpieces() if not self.piece_occluded(piece) ]

	def solve(self):
		return BacktrackingSolver(self).solve()

	def possible_movecnt(self):
		return len(list(self.possible_moves()))

	def dump(self):
		for piece in self.iterpieces():
			occluded = self.piece_occluded(piece)
			occlusionstr = " " if occluded else "!"
			print("%2d %2d %2d [%s]: %s" % (piece.dx, piece.dy, piece.dz, occlusionstr, piece))
			if occluded:
				for (occltype, occlusionpiece) in self.get_occlusions(piece):
					print("    %s-occl by %s" % (occltype, occlusionpiece))

		moves = list(self.possible_moves())
		print("Moves possible: %d" % (len(moves)))
		for (piece1, piece2) in moves:
			print("    * [%2d %2d %2d] <-> [%2d %2d %2d]"  % (piece1.dx, piece1.dy, piece1.dz, piece2.dx, piece2.dy, piece2.dz))


		for z in range(10):
			line = ""
			for x in range(10):
				stapel = self._piecedict[x][z].values()
				if len(stapel) == 0:
					line += "  "
				else:
					line += " %d" % (len(stapel))
			print(line)

	def valid_move(self, piece1, piece2):
		return (piece1.tileid == piece2.tileid) and (not self.piece_occluded(piece1)) and (not self.piece_occluded(piece2))

	def iterpieces(self):
		for zydict in list(self._piecedict.values()):
			for ydict in list(zydict.values()):
				yield from ydict.values()

