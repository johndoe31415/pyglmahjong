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

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import PIL.Image
import numpy
import ctypes
from Geo3d import Matrix4, Vector

class Shader(object):
	def __init__(self, shadertype, shaderfile, uniforms = None, attributes = None):
		self._stype = shadertype
		self._shader = glCreateShader(shadertype)
		shadersrc = open(shaderfile, "r").read()
		glShaderSource(self._shader, shadersrc)
		glCompileShader(self._shader)

		# Check if it compiled
		if glGetShaderiv(self._shader, GL_COMPILE_STATUS) != 1:
			print(shadersrc)
			raise Exception("Couldn't compile shader, error was: " + glGetShaderInfoLog(self._shader).decode("utf-8"))

	@property
	def glshader(self):
		return self._shader


class ShaderProgram(object):
	def __init__(self, *shaders):
		self._uniforms = { }
		self._attributes = { }
		self._active_uniforms = set()

		self._program = glCreateProgram()
		for shader in shaders:
			glAttachShader(self._program, shader.glshader)
		glLinkProgram(self._program)


		uniform_count = glGetProgramiv(self._program, GL_ACTIVE_UNIFORMS)
		for uniidx in range(uniform_count):
			uniformname = bytes(64)
			glGetActiveUniformName(self._program, uniidx, len(uniformname), None, ctypes.c_char_p(uniformname))
			uniformname = uniformname.rstrip(b"\x00").decode("utf-8")
			self._active_uniforms.add(uniformname)

		print("Compiled program uses %d uniforms, program info log: \"%s\"" % (len(self._active_uniforms), glGetProgramInfoLog(self._program)))


	def getuniformnames(self):
		return iter(self._active_uniforms)

	def _getattribute(self, name):
		if name not in self._attributes:
			position = glGetAttribLocation(self._program, name.encode("utf-8"))
			if (position is not None) and (position >= 0):
				self._attributes[name] = position
		return self._attributes.get(name)

	def _getuniform(self, name):
		if name not in self._uniforms:
			position = glGetUniformLocation(self._program, name.encode("utf-8"))
			if (position is not None) and (position >= 0):
				self._uniforms[name] = position
		return self._uniforms.get(name)

	def hasattribute(self, name):
		return self._getattribute(name) is not None

	def hasuniform(self, name):
		return self._getuniform(name) is not None

	def attribute(self, name):
		position = self._getattribute(name)
		if position is None:
			raise Exception("Tried to access non-existent attribute '%s'" % (name))
		return position

	def uniform(self, name):
		position = self._getuniform(name)
		if position is None:
			raise Exception("Tried to access non-existent uniform '%s'" % (name))
		return position

	def setactive(self):
		glUseProgram(self._program)

	def setinactive(self):
		glUseProgram(0)


class TextureCache(object):
	def __init__(self):
		self._cache = { }

	def _loadtex(self, texname):
		filename = texname
		img = PIL.Image.open(filename)
		if img.mode != "RGB":
			raise Expception("Texture is not in RGB format")
		img_data = img.tobytes()

		texid = glGenTextures(1)
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, texid)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
		return texid

	def _cachetex(self, texname):
		texid = self._loadtex(texname)
		self._cache[texname] = texid

	def __getitem__(self, texname):
		if texname not in self._cache:
			self._cachetex(texname)
		return self._cache[texname]

def compile_shader():
#	vertex_shader = Shader(GL_VERTEX_SHADER, "data/shaders/custom.vshader")
#	fragment_shader = Shader(GL_FRAGMENT_SHADER, "data/shaders/custom.fshader")
	vertex_shader = Shader(GL_VERTEX_SHADER, "data/shaders/std.vshader")
	fragment_shader = Shader(GL_FRAGMENT_SHADER, "data/shaders/std.fshader")
	shader_program = ShaderProgram(vertex_shader, fragment_shader)
	return shader_program

class GLObjectInstance(object):
	def __init__(self, glbufobj):
		self._glbufobj = glbufobj
		self._model = Matrix4.identity()
		self._texid = None
		self._uniforms = { }

	def updateuniforms(self, uniforms):
		uniforms.update(self._uniforms)
		uniforms["modelMatrix"] = self._model
		uniforms["modelViewProjMatrix"] = uniforms["projMatrix"]* uniforms["viewMatrix"] * self._model
		return uniforms

	def setuniform(self, **kwargs):
		self._uniforms.update(kwargs)

	@property
	def model(self):
		return self._model

	@model.setter
	def model(self, model):
		self._model = model

	@property
	def texid(self):
		return self._texid

	def settexture(self, texid):
		self._texid = texid

	@property
	def glbufobj(self):
		return self._glbufobj

class GLBufferedObject(object):
	def __init__(self, objtype, model_file):
		assert(objtype in [ GL_QUADS, GL_QUAD_STRIP, GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN, GL_TRIANGLES ])
		self._warnings = set()
		self._objtype = objtype
		self._program = compile_shader()

		interleaved_data = numpy.fromfile(model_file, dtype = numpy.float32)
		self._length = len(interleaved_data) // 8

		# Create a new VAO (Vertex Array Object) and bind it
		self._vao = glGenVertexArrays(1)
		glBindVertexArray(self._vao)

		# Generate buffers to hold our vertices
		self._vbuf = glGenBuffers(1)
		glBindBuffer(GL_ARRAY_BUFFER, self._vbuf)

		# Send the data over to the buffer
		glBufferData(GL_ARRAY_BUFFER, interleaved_data.nbytes, interleaved_data, GL_STATIC_DRAW)

		# Describe the position data layout in the buffer
		glEnableVertexAttribArray(self._program.attribute("vertex_ModelSpace"))
		glVertexAttribPointer(self._program.attribute("vertex_ModelSpace"), 3, GL_FLOAT, False, 32, ctypes.c_void_p(0))
		if self._program.hasattribute("normal_ModelSpace"):
			glEnableVertexAttribArray(self._program.attribute("normal_ModelSpace"))
			glVertexAttribPointer(self._program.attribute("normal_ModelSpace"), 3, GL_FLOAT, False, 32, ctypes.c_void_p(12))
		if self._program.hasattribute("vertex_TexCoords"):
			glEnableVertexAttribArray(self._program.attribute("vertex_TexCoords"))
			glVertexAttribPointer(self._program.attribute("vertex_TexCoords"), 2, GL_FLOAT, False, 32, ctypes.c_void_p(24))

		# Unbind the VAO first
		glBindVertexArray(0)

	def __call__(self):
		return GLObjectInstance(self)

	@staticmethod
	def _interleave(*arrays):
		assert(all(len(array) == len(arrays[0]) for array in arrays))
		rowsize = sum(len(array[0]) for array in arrays)
		result = numpy.empty((len(arrays[0]), rowsize), dtype = numpy.float32)
		target = [ ]
		for (index, row) in enumerate(zip(*arrays)):
			row = numpy.array([ item for sublist in row for item in sublist ], dtype = numpy.float32)
			result[index] = row
		return result

	def draw(self, uniforms):
		unprovided = self._program.getuniformnames() - uniforms.keys()
		if len(unprovided) > 0:
			for uniform in unprovided:
				if uniform not in self._warnings:
					print("Warning: Program uses uniform '%s' which was not provided (warning only shown once)." % (uniform))
					self._warnings.add(uniform)

		self._program.setactive()

		for (uniform, value) in uniforms.items():
			if not self._program.hasuniform(uniform):
				if uniform not in self._warnings:
					print("Ignored passed uniform '%s' (will show this message only once per object)" % (uniform))
					self._warnings.add(uniform)

				continue

			if isinstance(value, tuple) or isinstance(value, list):
				if len(value) == 2:
					glUniform2f(self._program.uniform(uniform), value[0], value[1])
				elif len(value) == 3:
					glUniform3f(self._program.uniform(uniform), value[0], value[1], value[2])
				else:
					raise Exception(NotImplemented)
			elif isinstance(value, Vector):
				glUniform3f(self._program.uniform(uniform), value.x, value.y, value.z)
			elif isinstance(value, Matrix4):
				glUniformMatrix4fv(self._program.uniform(uniform), 1, GL_FALSE, value.togl())
			elif isinstance(value, float):
				glUniform1f(self._program.uniform(uniform), value)
			else:
				raise Exception("Cannot deduce GL type for passed uniform %s '%s' (type %s)" % (uniform, str(value), str(type(value))))

		glBindVertexArray(self._vao)
		glDrawArrays(self._objtype, 0, self._length)
		glBindVertexArray(0)

		self._program.setinactive()

class GLBufferedObjects(object):
	def __init__(self):
		self._objs = [ ]
		self._uniforms = { }

	def add(self, obj):
		self._objs.append(obj)

	def setuniform(self, varname, value):
		self._uniforms[varname] = value

	def _getuniformsforobj(self, obj):
		uniforms = dict(self._uniforms)
		obj.updateuniforms(uniforms)
		return uniforms

	def draw(self):
		for obj in self._objs:
			uniforms = self._getuniformsforobj(obj)
			glActiveTexture(GL_TEXTURE0)
			glBindTexture(GL_TEXTURE_2D, obj.texid)
			obj.glbufobj.draw(uniforms)
#			glActiveTexture(GL_TEXTURE0)
#			glBindTexture(GL_TEXTURE_2D, 0)


