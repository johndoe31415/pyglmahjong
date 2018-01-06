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

import sys
import math
import time
import string
import numpy

from ViewPort import ViewPort
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from OpenGLTools import Shader, ShaderProgram, GLBufferedObject, GLBufferedObjects, TextureCache
from Tools import get_tuples, get_triplets
from Geo3d import Vector, Line, Plane, Quaternion, Matrix4
from Actions import MouseButton, MouseButtonEvent, MouseDragEvent, KeyboardKeyEvent

class OpenGLDisplay(object):
	def __init__(self):
		self._controller = None
		self._dirty = True
		self._matrix = {
			"proj":		None,
			"view":		None,
		}
		self._viewport = None
		self.reset_viewport()
		self._reshapeWindow(800, 600)
		self._movement = None
		self._mousepos = None
		self._arrows = [ ]
		self._cubes = [ ]
		self._global_uniforms = {
			"lightPos_WorldSpace":	Vector(0., 35, 0.),
			"LightPower":			835.,
			"SpecularExp":			5.,
		}
		self._movement_index = 0
		self._movement_types = {
			0: {
				"right":	"camera_yx",
				"middle":	"lightpower",
			},
			1: {
				"right":	"lightpos_xz",
				"middle":	"lightpos_y",
			},
		}

		glutInit(1, "None")
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_MULTISAMPLE)
		glEnable(GL_MULTISAMPLE)
		glutInitWindowSize(1024, 768)
		glutInitWindowPosition(1600 + 200, 200)

		window = glutCreateWindow(b"Python Mahjongg")

		glutDisplayFunc(self._drawGLScene)
		glutKeyboardFunc(self._keyPressed)
		glutMouseFunc(self._mousePressAction)
		glutMotionFunc(self._mouseDragAction)
		glutReshapeFunc(self._reshapeWindow)
		self._initGL()
		self._textures = TextureCache()
		self._idleFunc(0)

	def mark_dirty(self):
		self._dirty = True

	@property
	def textures(self):
		return self._textures

	def run(self, controller):
		self._controller = controller
		glutMainLoop()

	def _recalculate_viewmatrix(self):
		view = Matrix4.identity()
		view = view.translate(Vector(0, 0, -self._viewport.distance))
		view = view.rotate(self._viewport.anglex / 180 * math.pi, Vector(1, 0, 0))
		view = view.rotate(self._viewport.angley / 180 * math.pi, Vector(0, 1, 0))
		self._matrix["view"] = view
		self._dirty = True

	@property
	def viewport(self):
		return self._viewport

	@viewport.setter
	def viewport(self, viewport):
		self._viewport = viewport
		self._recalculate_viewmatrix()

	def reset_viewport(self):
		self.viewport = ViewPort(anglex = 65, angley = 0, distance = 18)

	def _initGL(self):
		glClearColor(0.95, 0.95, 0.95, 0.0)
		glClearDepth(1.0)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_TEXTURE_2D)
		glEnable(GL_CULL_FACE)
		glShadeModel(GL_SMOOTH)
		self._objectmodels = { }

	def get_object(self, name):
		return self._objectmodels[name]

	def load_object(self, name, binfile):
		self._objectmodels[name] = GLBufferedObject(GL_TRIANGLES, binfile)

	def _reshapeWindow(self, width, height):
		glViewport(0, 0, width, height)
		self._matrix["proj"] = Matrix4.perspective(45 / 180 * math.pi, width / height, 0.1, 100)
		self._dirty = True

	def _keyPressed(self, key, xpos, ypos):
		if len(key) == 1:
			decoded_key = key.decode("latin1")
			if decoded_key in string.printable:
				key = decoded_key
			else:
				decoded_key = {
					"\x1b":		"ESC",
					"\x08":		"BACKSPACE",
				}.get(decoded_key)
				if decoded_key is not None:
					key = decoded_key
		event = KeyboardKeyEvent(key = key, x = xpos, y = ypos)
		self._controller.keyboard_key_event(event)

	def _mouseDragAction(self, xpos, ypos):
		event = MouseDragEvent(x = xpos, y = ypos)
		self._controller.mouse_drag_event(event)

	def _getcoordsat(self, xpos, ypos):
		viewport = glGetIntegerv(GL_VIEWPORT)
		ypos = viewport[3] - ypos
		zpos = glReadPixels(xpos, ypos, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
		screencoords = Vector(xpos, ypos, zpos)
		worldcoords = Matrix4.unproject(screencoords, self._matrix["view"], self._matrix["proj"], viewport)
		return worldcoords

	def _mousePressAction(self, button, action, xpos, ypos):
		mouse_button = MouseButton(button)
		action = {
			0:	"press",
			1:	"release",
		}[action]

		world = self._getcoordsat(xpos, ypos)

		event = MouseButtonEvent(button = mouse_button, x = xpos, y = ypos, action = action, world = world)
		self._controller.mouse_button_event(event)

	def get_uniform(self, name):
		return self._global_uniforms[name]

	def set_uniform(self, name, value):
		self._global_uniforms[name] = value

	def _drawGLScene(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		if self._controller is not None:
			sceneobjects = self._controller.get_scene_objects()
			for (uniformname, value) in self._global_uniforms.items():
				sceneobjects.setuniform(uniformname, value)
			sceneobjects.setuniform("projMatrix", self._matrix["proj"])
			sceneobjects.setuniform("viewMatrix", self._matrix["view"])
			sceneobjects.draw()

		try:
			glutSwapBuffers()
		except KeyboardInterrupt:
			sys.exit(0)

	def _idleFunc(self, arg):
		glutTimerFunc(33, self._idleFunc, 0)
		if self._dirty:
			self._drawGLScene()
			self._dirty = False

	def quit(self):
		glutLeaveMainLoop()
