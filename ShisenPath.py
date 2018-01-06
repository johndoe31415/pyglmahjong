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

import random

class ShisenPath(object):
	def __init__(self, points):
		self._points = points

	def getpoints(self):
		return iter(self._points)

	def walk(self):
		for ((x1, y1), (x2, y2)) in zip(self._points, self._points[1:]):
			if (x1 == x2) and (y1 == y2):
				continue

			if x1 == x2:
				step = 1 if y1 < y2 else -1
				for y in range(y1, y2, step):
					if (x1, y) != self._points[0]:
						yield (x1, y)
			else:
				step = 1 if x1 < x2 else -1
				for x in range(x1, x2, step):
					if (x, y1) != self._points[0]:
						yield (x, y1)

	def __str__(self):
		return str(self._points)

class ShisenConnection(object):
	def __init__(self, x1, y1, x2, y2, minx, miny, maxx, maxy):
		(self._x1, self._y1) = (x1, y1)
		(self._x2, self._y2) = (x2, y2)
		(self._minx, self._miny) = (minx, miny)
		(self._maxx, self._maxy) = (maxx, maxy)


	def paths(self):
		# Bipaths (and direct paths)
		yield ShisenPath([ (self._x1, self._y1), (self._x1, self._y2), (self._x2, self._y2) ])
		yield ShisenPath([ (self._x1, self._y1), (self._x2, self._y1), (self._x2, self._y2) ])

		# Tripaths
		if self._x1 != self._x2:
			for offset in range(1, self._maxy - self._y1 + 2):
				yield ShisenPath([ (self._x1, self._y1), (self._x1, self._y1 + offset), (self._x2, self._y1 + offset), (self._x2, self._y2) ])

			for offset in range(1, self._y1 - self._miny + 2):
				yield ShisenPath([ (self._x1, self._y1), (self._x1, self._y1 - offset), (self._x2, self._y1 - offset), (self._x2, self._y2) ])

		if self._y1 != self._y2:
			for offset in range(1, self._maxx - self._x1 + 2):
				yield ShisenPath([ (self._x1, self._y1), (self._x1 + offset, self._y1), (self._x1 + offset, self._y2), (self._x2, self._y2) ])

			for offset in range(1, self._x1 - self._minx + 2):
				yield ShisenPath([ (self._x1, self._y1), (self._x1 - offset, self._y1), (self._x1 - offset, self._y2), (self._x2, self._y2) ])


if __name__ == "__main__":
	def path_plausible(pathpts, start, end):
		if any(point == start for point in pathpts):
			return "StartInc"
		if any(point == end for point in pathpts):
			return "EndInc"

		for (pt1, pt2) in zip(pathpts, pathpts[1:]):
			diff = abs(pt1[0] - pt2[0]) + abs(pt1[1] - pt2[1])
			if diff != 1:
				return "Diff=%d" % (diff)

		if len(pathpts) > 0:
			firstpt = pathpts[0]
			diff = abs(firstpt[0] - start[0]) + abs(firstpt[1] - start[1])
			if diff != 1:
				return "NotAtStart"

			lastpt = pathpts[-1]
			diff = abs(lastpt[0] - end[0]) + abs(lastpt[1] - end[1])
			if diff != 1:
				return "NotAtEnd"
		else:
			diff = abs(end[0] - start[0]) + abs(end[1] - start[1])
			if diff != 1:
				return "NotNext"

		if any(point[0] < -1 for point in pathpts):
			return "X < MinX"

		if any(point[0] > 16 for point in pathpts):
			return "X > MaxX"

		if any(point[1] < -1 for point in pathpts):
			return "Y < MinY"

		if any(point[1] > 16 for point in pathpts):
			return "Y > MaxY"

		return "OK"


	for i in range(1000):
		start = (random.randrange(16), random.randrange(16))
		end = (random.randrange(16), random.randrange(16))
		if start == end:
			continue
		scon = ShisenConnection(start[0], start[1], end[0], end[1], 0, 0, 15, 15)
		for path in scon.paths():
			points = list(path.walk())
			plausible = path_plausible(points, start, end)
			if plausible != "OK":
				print("Path from", start, "to", end)
				print(path, plausible)
				for point in path.walk():
					print(point)
				print()


