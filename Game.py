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
import itertools
import random

from TileSet import Tile
from Piece import Piece

class Game(object):
	def __init__(self, config, layout, tileset, board):
		self._config = config
		self._layout = layout
		self._center = self._layout.center()
		self._tileset = tileset
		self._board = board
		self._spacing = 1.02
		self._selected_piece = None

	def gettexturefile(self, texname):
		return self._tileset.gettexturefile(self._config.texpath, self._config.texresolution, texname)

	def _centercoords(self, dx, dy, dz):
		x = (dx - self._layout.gridlen * self._center[0]) * Piece.WIDTH * self._spacing * self._layout.grid + Piece.WIDTH / 2
		y = dy * Piece.HEIGHT
		z = (dz - self._layout.gridlen * self._center[2]) * Piece.LENGTH * self._spacing * self._layout.grid + Piece.LENGTH / 2
		return (x, y, z)

	def _make_piece(self, gridpiece, tile):
		(x, y, z) = self._centercoords(gridpiece.dx, gridpiece.dy, gridpiece.dz)
		return Piece(x, y, z, gridpiece = gridpiece, tile = tile)

	def reset(self):
		self._board.clear()
		for (index, gridpiece) in enumerate(self._layout.iterpieces()):
			self._board.add_piece(self._make_piece(gridpiece, Tile(tileid = 0, name = None, face = "circle_1")))

	def _set_layout(self, gridpieces, tiles):
		assert(len(gridpieces) == len(list(tiles)))
		self._board.clear()
		for (gridpiece, tile) in zip(gridpieces, tiles):
			self._board.add_piece(self._make_piece(gridpiece, tile))

	def _set_seeded_layout(self, seed):
		tsiter = self._tileset.iterator(len(self._layout))
		gridpieces = list(self._layout.iterpieces())
		tiles = list(tsiter.getrandtiles(seed))
		self._set_layout(gridpieces, tiles)

	def _set_random_layout(self):
		seed = random.randrange(2 ** 32)
		self._set_seeded_layout(seed)
		return seed

	def new(self):
		if (len(self._layout) % 2) == 0:
			if self._config.seed is None:
				tries = 0
				while True:
					tries += 1
					seed = self._set_random_layout()
					print("Try #%d seed %d" % (tries, seed))
					naively_solvable = self._board.naively_solvable()
					if self._config.allow_unsolvable or naively_solvable:
						break
			else:
				seed = self._config.seed
				self._set_seeded_layout(seed)
				naively_solvable = self._board.naively_solvable()
			print("Game started, possible moves: %d (naively solvable %s)" % (self._board.possible_movecnt(), naively_solvable))
			print("Seed: %d" % (seed))
		else:
			# Never solvable!
			self.reset()

#		TODO Mahjong-spezifisch
#		self.reset()
#		order = [ ]
#		while self._board.piececnt > 0:
#			nextpcs = random.sample(self._board.nonoccludedpieces(), 2)
#			for nextpc in nextpcs:
#				self._board.remove_piece(nextpc)
#			order += nextpcs
#
#		tsiter = self._tileset.iterator(2)
#		tiles = list(tsiter.gettiles(len(self._layout)))
#		for (piece, tile) in zip(order, tiles):
#			self._board.add_piece(self._make_piece(piece.gridpiece, tile))

	def _set_all_pieces_idle(self):
		for piece in self.iterpieces():
			piece.setstate("idle")

	def clickpiece(self, piece):
		self._set_all_pieces_idle()
		if self._board.piece_selectable(piece):
			if (self._selected_piece is None) or (self._selected_piece.tileid != piece.tileid):
				# First selected piece or unmatching piece
				piece.setstate("selected")
				self._selected_piece = piece
			elif (self._selected_piece != piece):
				validmove = self._board.valid_move(piece, self._selected_piece)
				# Second piece, valid move, remove matching tiles
				if validmove:
					self._board.remove_piece(self._selected_piece)
					self._board.remove_piece(piece)
					self._selected_piece = None
					print("Remaining moves: %d" % (self._board.possible_movecnt()))
					if not isinstance(validmove, bool):
						return [ self._centercoords(x, 0, y) for (x, y) in validmove ]
			else:
				# Deselect piece
				self._selected_piece = None
		else:
			# Selection not possible, piece is occluded
			self._selected_piece = None
			piece.setstate("occluded")
			for (occltype, occludingpiece) in self._board.get_occlusions(piece):
				occludingpiece.setstate("occludes")

	def iterpieces(self):
		return self._board.iterpieces()

	def solve(self):
		return self._board.solve()

