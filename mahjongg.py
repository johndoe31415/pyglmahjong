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

import os
import sys

from FriendlyArgumentParser import FriendlyArgumentParser
from Game import Game
from Layout import Layout
from TileSet import TileSet
from MahjongBoard import MahjongBoard
from ShisenBoard import ShisenBoard
from OpenGLDisplay import OpenGLDisplay
from GameController import GameController

class Configuration(object):
	def __init__(self, args):
		self._args = args

	@property
	def datadir(self):
		if self._args.datadir is None:
			executable_dir = os.path.dirname(os.path.realpath(sys.argv[0])) + "/"
			return executable_dir + "data/"
		else:
			return self._args.datadir

	@property
	def layout(self):
		if self._args.layout is not None:
			return self._args.layout
		else:
			return {
				"mahjong":	"easy",
				"shisen":	"14x6",
			}[self._args.game]

	@property
	def texpath(self):
		return self.datadir + "textures/"

	@property
	def tilesetfile(self):
		return self.datadir + "tileset/" + self._args.tileset + ".xml"

	@property
	def layoutfile(self):
		return self.datadir + "layout/" + self._args.game + "/" + self.layout + ".xml"

	def __getattr__(self, name):
		return getattr(self._args, name)

parser = FriendlyArgumentParser()
parser.add_argument("--datadir", metavar = "path", type = str, default = None, help = "Specifies directory in which the data files are located. Defaults to data/ relative to executable.")
parser.add_argument("-g", "--game", choices = [ "mahjong", "shisen" ], default = "mahjong", help = "Specifies which game to play")
parser.add_argument("-t", "--tileset", metavar = "name", default = "default", help = "Name of the tileset to use. Defaults to %(default)s")
parser.add_argument("-l", "--layout", metavar = "name", help = "Name of the board layout to use.")
parser.add_argument("-s", "--seed", metavar = "seed", type = int, help = "Seed of the game to use. Randomly chosen if omitted.")
parser.add_argument("--texresolution", metavar = "res", type = int, default = 512, help = "Specify texture resolution that should be used. Default is %(default)s.")
parser.add_argument("--allow-unsolvable", action = "store_true", default = False, help = "Allow non-solvable board layouts.")
args = parser.parse_args(sys.argv[1:])

config = Configuration(args)
layout = Layout(config.layoutfile)
tileset = TileSet(config.tilesetfile)
if args.game == "mahjong":
	board = MahjongBoard(layout.gridlen)
elif args.game == "shisen":
	board = ShisenBoard()
else:
	raise Exception(NotImplemented)
game = Game(config, layout, tileset, board)
game.new()

display = OpenGLDisplay()

gamecontroller = GameController(args, game, display)


