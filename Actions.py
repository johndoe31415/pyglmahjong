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

import enum
import collections

class MouseButton(enum.Enum):
	LEFT = 0
	MIDDLE = 1
	RIGHT = 2
	WHEEL_UP = 3
	WHEEL_DOWN = 4
	EXTRA_5 = 5
	EXTRA_6 = 6
	EXTRA_7 = 7
	EXTRA_8 = 8
	EXTRA_9 = 9

MouseButtonEvent = collections.namedtuple("MouseButtonEvent", [ "button", "action", "x", "y", "world" ])
MouseDragEvent = collections.namedtuple("MouseDragEvent", [ "x", "y" ])

KeyboardKeyEvent = collections.namedtuple("KeyboardKeyEvent", [ "key", "x", "y" ])
