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

import hashlib

class PRNG(object):
	def __init__(self, seed):
		self._seed = bytes([ (seed >> (8 * i)) & 0xff for i in range(16) ])
		self.nextval()

	def nextval(self):
		rndval = sum([ value << (i * 8) for (i, value) in enumerate(self._seed[:8]) ])
		self._seed = hashlib.md5(self._seed).digest()
		return rndval

	def shuffle(self, rndlist):
		for i in reversed(range(1, len(rndlist))):
			j = self.nextval() % (i + 1)
			tmp = rndlist[i]
			rndlist[i] = rndlist[j]
			rndlist[j] = tmp

if __name__ == "__main__":
	import collections

	listlen = 10
	frequency = collections.defaultdict(collections.Counter)
	for i in range(100000):
		x = PRNG(0x12345678 + i)
		mylist = list(range(listlen))
		x.shuffle(mylist)

		for i in range(listlen):
			frequency[i].update([ mylist[i] ])

	for i in range(listlen):
		line = "%d: " % (i)
		for j in range(listlen):
			line += "%7d " % (frequency[i][j])
		print(line)
