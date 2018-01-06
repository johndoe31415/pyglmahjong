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
from PRNG import PRNG

Tile = collections.namedtuple("Tile", [ "tileid", "name", "face" ])

class TileSetIterator(object):
	def __init__(self, tileset, tilecount):
		self._tileset = tileset
		self._tilecount = tilecount
		if (tilecount % 2) != 0:
			raise Exception("Tile count %d not divisible by 2." % (tilecount))

	def getpairs(self):
		for i in range(self._tilecount // 2):
			nexttiles = self._tileset[i % len(self._tileset)]
			yield tuple(nexttiles)

	def gettiles(self):
		for pair in self.getpairs():
			yield pair[0]
			yield pair[1]

	def getrandtiles(self, seed):
		prng = PRNG(seed)
		tilelist = list(self.gettiles())
		prng.shuffle(tilelist)
		for tile in tilelist:
			yield tile

class TileSet(object):
	def __init__(self, filename):
		xml = XMLParser().parsefile(filename)
		self._matchingtiles = [ ]
		for matchingtiles in xml.matchingtiles:
			tiles = [ ]
			for tile in matchingtiles.tile:
				tiles.append(Tile(name = tile["name"], tileid = 100 + len(self._matchingtiles), face = tile["name"]))
			if len(tiles) == 1:
				tiles.append(tiles[0])
			elif len(tiles) == 2:
				pass
			else:
				raise Exception(NotImplemented)
			self._matchingtiles.append(tiles)

	def gettexturefile(self, path, resolution, face):
		return path + "pieces/" + str(resolution) + "/" + face + ".jpg"

	def iterator(self, tilecount):
		return TileSetIterator(self, tilecount)

	def __getitem__(self, index):
		return self._matchingtiles[index]

	def __len__(self):
		return len(self._matchingtiles)

	def __str__(self):
		return "TileSet<%d pcs>" % (len(self))

if __name__ == "__main__":
	ts = TileSet("data/tileset/debug.xml")
	tsi = ts.iterator(42)
	for tile in tsi.getrandtiles(12345):
		print(tile)
