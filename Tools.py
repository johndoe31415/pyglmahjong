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

def get_nlets(n, array, wraparound):
	maxval = len(array)
	if not wraparound:
		maxval = maxval - n + 1
	for i in range(maxval):
		yield tuple(array[(i + j) % len(array)] for j in range(n))

def get_tuples(array, wraparound = False):
	return get_nlets(2, array, wraparound)

def get_triplets(array, wraparound = False):
	return get_nlets(3, array, wraparound)

if __name__ == "__main__":
	print(list(get_nlets(3, "foobar", True)))
