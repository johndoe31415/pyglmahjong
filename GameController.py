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

from OpenGLTools import GLBufferedObjects
from ViewPort import ViewPort
from Actions import MouseButton

class GameController(object):
	_MOUSESPEED = 0.5
	_ZOOM_DISTANCE = 1
	_MIDDLE_MOUSE_ACTIONS = [ "lightpos_xz", "lightpos_y", "lightpower" ]

	def __init__(self, args, game, display):
		self._args = args
		self._game = game
		self._display = display

		self._movement = None
		self._mousepos = None
		self._middle_mouse_actionidx = 0

		self._display.load_object("piece", "data/models/piece.bin")
		self._display.run(self)

	def _getpieceat(self, worldcoords):
		(closest, mindist) = (None, None)
		for piece in self._game.iterpieces():
			piecepos = piece.getcenter()
			dist = (piecepos - worldcoords).length()
			if (closest is None) or (dist < mindist):
				mindist = dist
				closest = piece
		if mindist < 1:
			return closest

	def mouse_button_event(self, event):
		print("Mouse button", event)
		if event.button == MouseButton.RIGHT:
			if event.action == "release":
				self._movement = None
				self._mousepos = None
			else:
				self._movement = "camera_yx"
				self._mousepos = event
		elif event.button == MouseButton.MIDDLE:
			if event.action == "release":
				self._movement = None
				self._mousepos = None
			else:
				action = self._MIDDLE_MOUSE_ACTIONS[self._middle_mouse_actionidx]
				self._movement = action
				self._mousepos = event
		elif event.button == MouseButton.LEFT:
			if event.action == "press":
				piece = self._getpieceat(event.world)
				if piece is not None:
					self._game.clickpiece(piece)
					self._display.mark_dirty()
		elif event.button == MouseButton.WHEEL_DOWN:
			# Zoom out
			self._display.viewport = ViewPort(anglex = self._display.viewport.anglex, angley = self._display.viewport.angley, distance = self._display.viewport.distance + self._ZOOM_DISTANCE)
		elif event.button == MouseButton.WHEEL_UP:
			# Zoom in
			self._display.viewport = ViewPort(anglex = self._display.viewport.anglex, angley = self._display.viewport.angley, distance = self._display.viewport.distance - self._ZOOM_DISTANCE)

	def mouse_drag_event(self, event):
		print("Mouse drag", event)
		if self._movement is not None:
			if self._mousepos is not None:
				movementu = (event.x - self._mousepos.x) * self._MOUSESPEED
				movementv = (event.y - self._mousepos.y) * self._MOUSESPEED
				if self._movement == "camera_yx":
					self._display.viewport = ViewPort(anglex = self._display.viewport.anglex + movementv, angley = self._display.viewport.angley + movementu, distance = self._display.viewport.distance)
				elif self._movement == "lightpos_xz":
					self._display.set_uniform("lightPos_WorldSpace", self._display.get_uniform("lightPos_WorldSpace").affect("xz", movementu * 0.25, movementv * 0.25))
				elif self._movement == "lightpos_y":
					self._display.set_uniform("lightPos_WorldSpace", self._display.get_uniform("lightPos_WorldSpace").affect("y", movementv * 0.25))
				elif self._movement == "lightpower":
					self._display.set_uniform("SpecularExp", self._display.get_uniform("SpecularExp") + movementu * 0.25)
					self._display.set_uniform("LightPower", self._display.get_uniform("LightPower") * (1 - (movementv * 0.01)))
					print("Power %4.0f Specular %5.3f" % (self._display.get_uniform("LightPower"), self._display.get_uniform("SpecularExp")))
				else:
					print("Unknown movement direction", self._movement)
				self._display.mark_dirty()
				self._mousepos = event

	def keyboard_key_event(self, event):
		print("Keyboard", event)
		if event.key == "ESC":
			self._display.quit()
		elif event.key == "q":
			self._middle_mouse_actionidx = (self._middle_mouse_actionidx + 1) % len(self._MIDDLE_MOUSE_ACTIONS)
			print("Middle mouse action: %s" % (self._MIDDLE_MOUSE_ACTIONS[self._middle_mouse_actionidx]))

	def _drawPiece(self, piece):
		if piece.state == "idle":
			aval = piece.gridpiece.dy / 4 * 0.35
			if aval >= 0.35:
				aval = 0.35
			ambient = (aval, aval, aval)
			ambient_top = ambient
		elif piece.state == "selected":
			ambient = (0.25, 0.45, 0.25)
			ambient_top = (0.45, 0.6, 0.45)
		elif piece.state == "occluded":
			ambient = (0.6, 0.0, 0.0)
			ambient_top = ambient
		elif piece.state == "occludes":
			ambient = (0.3, 0.1, 0.1)
			ambient_top = ambient
		else:
			raise Exception("Unknown state %s!" % (piece.state))

		if piece.globject is None:
			globject = self._display.get_object("piece")()
			globject.model = globject.model.translate(piece)
			globject.settexture(self._display.textures[self._game.gettexturefile(piece.face)])
			piece.setglobject(globject)

		piece.globject.setuniform(ambientLight = ambient)
		return piece.globject

	def get_scene_objects(self):
		sceneobjects = GLBufferedObjects()
		for piece in self._game.iterpieces():
			sceneobjects.add(self._drawPiece(piece))
		return sceneobjects
