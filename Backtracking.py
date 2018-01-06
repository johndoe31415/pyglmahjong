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

class BacktrackingSolvable(object):
	"""Interface that needs to be implemented in order to be solvable by the
	BacktrackingSolver."""
	def backtrack_clone(self):
		raise Exception(NotImplemented)

	def backtrack_condition_satisfied(self):
		raise Exception(NotImplemented)

	def backtrack_makechoice(self, choice):
		raise Exception(NotImplemented)

	def backtrack_reversechoice(self, choice):
		raise Exception(NotImplemented)

	def backtrack_choices(self):
		raise Exception(NotImplemented)

class BacktrackingSolver(object):
	def __init__(self, initialstate):
		if not isinstance(initialstate, BacktrackingSolvable):
			raise Exception("Given state is not BacktrackingSolvable.")
		self._initstate = initialstate

	def solve(self):
		state = self._initstate.backtrack_clone()
		moves = [ ]
		choices = [  ]

		iters = 0
		while True:
			solvestate = state.backtrack_condition_satisfied()
			if solvestate:
				# Solution found
				break
			elif solvestate is None:
				# Unsolvable from here on, backtrack
				state.backtrack_reversechoice(moves.pop())
			else:
				# No solution found yet, continue to get choices
				choices.append(list(state.backtrack_choices()))
			while len(choices[-1]) == 0:
				# No more choices, backtrack
				if len(moves) == 0:
					# Completely unsolvable
					return
				state.backtrack_reversechoice(moves.pop())
				choices.pop()

			iters += 1
			if (iters % 1000) == 0:
				print(state.piececnt)

			# Perform a choice
			choice = choices[-1].pop()
			moves.append(choice)
			state.backtrack_makechoice(choice)
		return moves

