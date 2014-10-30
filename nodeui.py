#!/usr/bin/env python3
import pyglet, pickle
from pyglet.gl import *
from threading import *
from os.path import isfile, abspath
from collections import OrderedDict as OD
from time import time
from json import loads, dumps
from base64 import b64encode, b64decode

pyglet.options['audio'] = ('alsa', 'openal', 'silent')
key = pyglet.window.key

def decompress(data):
	try:
		return zlib.decompress(data)
	except:
		return b'{"Error" : "Decompressing string"}'

def b(x):
	if type(x) == str: return bytes(x, 'UTF-8')
	return x

def serialize(data):
	return b64encode(b(data))

def deserialize(data):
	return b64decode(b(data))

def depickle(data):
	return pickle.loads(data)

def dopickle():
	""" To be implemented if found useful """
	pass

def colorConverter(r,g,b,a=255):
	r = (1.0/255)*r
	g = (1.0/255)*g
	b = (1.0/255)*b
	a = (1.0/255)*a
	return r,g,b,a

def mainThread():
	""" Returns (none or) a handle to the main "thread" object. """ 
	for t in enumerate():
		if t.name == 'MainThread':
			return t
	return None

class GenericObject(pyglet.sprite.Sprite):
	def __init__(self, texture=None, width=None, height=None, color="#C2C2C2", x=0, y=0, anchor=None, scale=1.0):
		if texture and isfile(texture):
			self.texture = pyglet.image.load(texture)
		else:
			## If no texture was supplied, we will create one
			if width is None:
				width = 60
			if height is None:
				height = 60
			self.texture = self.gen_solid_img(width, height, color, alpha=255)

		## We must instanciate pyglet.sprite.Sprite before
		## doing anything else because otherwise x, y, scale etc
		## will be overwritten or not accessible in Python3.
		## (Python2 would work fine as long as supplied as an inheritance)
		super(GenericObject, self).__init__(self.texture)
		if scale:
			self.scale = scale
		elif width and width < self.texture.width:
			self.scale = (1.0/max(width, self.texture.width))*min(width, self.texture.width)
		elif height and height < self.texture.height:
			self.scale = (1.0/max(height, self.texture.height))*min(height, self.texture.height)

		self.anchor = anchor
		if anchor == 'center':
			self.image.anchor_x = self.image.width / 2
			self.image.anchor_y = self.image.height / 2

		self.x = x
		self.y = y

		self.triggers = {'hover' : False}

	def swap_image(self, image, filePath=True, width=None):
		try:
			if isfile(image):
				self.texture = pyglet.image.load(abspath(image))
			else:
				self.texture = image
		except:
			return False
		
		self.image = self.texture
		if width and width < self.texture.width:
			self.scale = (1.0/max(width, self.texture.width))*min(width, self.texture.width)
		elif height and height < self.texture.height:
			self.scale = (1.0/max(height, self.texture.height))*min(height, self.texture.height)

	def gen_solid_img(self, width, height, c, alpha=255):
		if '#' in c:
			c = c.lstrip("#")
			c = max(6-len(c),0)*"0" + c
			r = int(c[:2], 16)
			g = int(c[2:4], 16)
			b = int(c[4:], 16)
			c = (r,g,b,alpha)#int(0.2*255))
		return pyglet.image.SolidColorImagePattern(c).create_image(width,height)

	def draw_line(self, to, color=(0.2, 0.2, 0.2, 1)):
		if type(to) == GenericObject:
			xy, dxy = (self.x+self.width/2, self.y+self.height/2), (to.x+to.width/2, to.y+to.height/2)
		elif type(to) == tuple:
			xy, dxy = to
		else:
			return None

		glColor4f(color[0], color[1], color[2], color[3])
		glBegin(GL_LINES)
		glVertex2f(xy[0], xy[1])
		glVertex2f(dxy[0], dxy[1])
		glEnd()

	def draw_border(self, color=(0.2, 0.2, 0.2, 0.5)):
		""" Current limitations are that this only draws a border around the object itself. """
		self.draw_line((self.x, self.y), (self.x, self.y+self.height+1), color)
		self.draw_line((self.x, self.y+self.height+1), (self.x+self.width+1, self.y+self.height+1), color)
		self.draw_line((self.x+self.width+1, self.y+self.height+1), (self.x+self.width+1, self.y), color)
		self.draw_line((self.x+self.width+1, self.y), (self.x, self.y), color)

	def pixels_to_vertexlist(self, pixels):
		# Outdated pixel conversion code
		vertex_pixels = []
		vertex_colors = []

		for pixel in pixels:
			vertex = list(pixel)
			vertex_pixels += vertex[:-1]
			vertex_colors += list(vertex[-1])

		# Old pyglet versions (including 1.1.4, not including 1.2
		# alpha1) throw an exception if vertex_list() is called with
		# zero vertices. Therefore the length must be checked before
		# calling vertex_list().
		#
		# TODO: Remove support for pyglet 1.1.4 in favor of pyglet 1.2.
		if len(pixels):
			return pyglet.graphics.vertex_list(
				len(pixels),
				('v2i', tuple(vertex_pixels)),
				('c4B', tuple(vertex_colors)))
		else:
			return None

	def clean_vertexes(self, *args):
		clean_list = []
		for pair in args:
			clean_list.append((int(pair[0]), int(pair[1])))
		return clean_list

	def draw_square(self, bottom_left, top_left, top_right, bottom_right, color=(0.2, 0.2, 0.2, 0.5)):
		#glColor4f(0.2, 0.2, 0.2, 1)
		#glBegin(GL_LINES)

		bottom_left, top_left, top_right, bottom_right = self.clean_vertexes(bottom_left, top_left, top_right, bottom_right)

		c = (255, 255, 255, 128)

		window_corners = [
			(bottom_left[0],bottom_left[1],c),	# bottom left
			(top_left[0],top_left[1],c),	# top left
			(top_right[0],top_right[1],c),	# top right
			(bottom_right[0],bottom_right[1],c)		# bottom right
		]

		box_vl = self.pixels_to_vertexlist(window_corners)
		box_vl.draw(pyglet.gl.GL_QUADS)
		#glEnd()

	def draw_header(self):
		"""
		A simplistic function used to draw a square-shaped header.


			size = 15
			glPointSize(size)
			glColor4f(0.2, 0.2, 0.2, 0.5)
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			glBegin(GL_POINTS)
	
			for x in range(self.x, self.x+self.width+size, size):
				for y in range(self.y, self.y+self.height, size):
					glVertex2f(x, y)
			glEnd()"""
		self.draw_square((self.x, self.y), (self.x, self.y+self.height), (self.x+self.width, self.y+self.height), (self.x+self.width, self.y))

	def rotate(self, deg):
		self.image.anchor_x = self.image.width / 2
		self.image.anchor_y = self.image.height / 2
		self.rotation = self.rotation+deg
		if self.anchor != 'center':
			self.image.anchor_x = 0
			self.image.anchor_y = 0
		return True

	def fade_in(self):
		self.opacity += 10
		if self.opacity > 255:
			self.opacity = 255

	def fade_out(self):
		self.opacity -= 2.5
		if self.opacity < 0:
			self.opacity = 0


	def click_check(self, x, y):
		"""
		When called, returns self (the object)
		to the calling-origin as a verification
		that we pressed inside this object, and
		by sending back self (the object) the caller
		can interact with this object or we can
		overhook this function in a private class
		and return inside objects to the caller
		as a "redirection" (useful for buttons inside
			windows etc)
		"""
		if self.x < x < self.x+self.width:
			if self.y < y < self.y+self.height: return self

	def click(self, x, y, merge=None):
		"""
		Usually click_check() is called followed up
		with a call to this function.
		Basically what this is, is that a click
		should occur within the object.
		Normally a class who inherits Spr() will create
		their own click() function but if none exists
		a default must be present.
		"""
		return True

	def right_click(self, x, y, merge):
		"""
		See click(), same basic concept
		"""
		return True

	def hover(self, x, y):
		"""
		See click(), same basic concept
		"""
		self.triggers['hover'] = True
		return True

	def hover_out(self, x, y):
		"""
		See click(), same basic concept
		"""
		self.triggers['hover'] = False
		return True

	def type(self, what):
		"""
		Type() is called from main() whenever a key-press
		has occured that is type-able.
		Meaning whenever a keystroke is made and it was
		of a character eg. A-Z it will be passed as a str()
		representation to type() that will handle the character
		in a given manner.
		This function doesn't process anything but will need
		to be here in case a class that inherits Spr() doesn't
		have their own function for it (which, they should...) 
		"""
		return True

	def gettext(self):
		return ''

	def on_close(self):
		self.has_exit = True
		self.set_visible(False)
		self.close()

	def move(self, x, y):
		self.x += x
		self.y += y

	def _draw(self):
		"""
		Normally we call _draw() instead of .draw() on sprites
		because _draw() will contains so much more than simply
		drawing the object, it might check for interactions or
		update inline data (and most likely positioning objects).
		"""
		self.draw()



class main(pyglet.window.Window):
	def __init__ (self,):
		super(main, self).__init__(800, 600, fullscreen = False, caption='Shatter')
		self.bg = GenericObject(width=800, height=600, color=(228,228,228,255))

		self.sprites = OD()
		#self.lines = OD()
		self.mergeMap = OD()
		
		self.drag = False
		self.active = None, None
		self.alive = 1
		self.multiselect = False

		self.modifiers = {'shift' : False}

		self.build_initial_nodes()

	def on_draw(self):
		self.render()

	def on_close(self):
		self.alive = 0

	def build_initial_nodes(self):
		self.sprites = OD()
		# ...

	def on_mouse_motion(self, x, y, dx, dy):
		for sprite_name, sprite in self.sprites.items():
			if sprite:
				sprite_obj = sprite.click_check(x, y)
				if sprite_obj:
					sprite_obj.hover(x, y)
				else:
					sprite.hover_out(x, y)

	# def link_objects(self, start, end):
	# 	start_obj, end_obj = None, None
	# 	for sprite_name, sprite in self.sprites.items():
	# 		if sprite and sprite_name not in ('2-loading'):
	# 			if sprite.click_check(start[0], start[1]):
	# 				start_obj = sprite_name, sprite
	# 			if sprite.click_check(end[0], end[1]):
	# 				end_obj = sprite_name, sprite

	# 	del(self.lines['link'])
	# 	if start_obj and end_obj and end_obj[0] != start_obj[0]:
	# 		start_obj[1].link(end_obj[1])

	def on_mouse_release(self, x, y, button, modifiers):
		if button == 1:
			if self.active[1] and not self.drag and self.multiselect == False:
				self.active[1].click(x, y, self.mergeMap)
				if self.active[0] == 'menu':
					del(self.sprites['menu'])
			self.drag = False
			if 'link' in self.lines:
				##   link_objects( lines == ((x, y), (x, y)) )
				self.link_objects(self.lines['link'][0], self.lines['link'][1])
		elif button == 4:
			if not self.active[0]:
				pass #Do something on empty spaces?
			else:
				self.active[1].right_click(x, y, self.mergeMap)
			#self.sprites['temp_vm'] = virtualMachine(pos=(x-48, y-48))
			#self.requested_input = self.sprites['temp_vm'].draws['1-title']
			#self.sprites['input'] = Input("Enter the name of your virtual machine", pos=(int(self.width/2-128), int(self.height/2-60)), height=120)

		#if type(self.active[1]) != Input:
		#	self.active = None, None
	
	def on_mouse_press(self, x, y, button, modifiers):
		if button == 1 or button == 4:
			for sprite_name, sprite in self.sprites.items():
				if sprite:
					sprite_obj = sprite.click_check(x, y)
					if sprite_obj:
						self.active = sprite_name, sprite_obj
						if button == 1:
							if self.multiselect != False:
								if sprite_name not in self.multiselect:
										self.multiselect.append(sprite_name)

	def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
		self.drag = True
		if self.active[1] and self.multiselect == False and hasattr(self.active[1], 'link'):
			self.lines['link'] = ((self.active[1].x+(self.active[1].width/2), self.active[1].y+(self.active[1].height/2)), (x,y))
		elif self.multiselect:
			for obj in self.multiselect:
				self.sprites[obj].move(dx, dy)

	def on_key_release(self, symbol, modifiers):
		if symbol == key.LCTRL:
			self.multiselect = False

	def on_key_press(self, symbol, modifiers):
		if symbol == 65307: # [ESC]
			self.alive = 0
		
		elif symbol == key.LSHIFT:
			self.modifiers['shift'] = True

		elif self.active[1] and hasattr(self.active[1], 'input') and hasattr(self.active[1], 'gettext'):
			if symbol == key.SPACE:
				pass
				#if self.active[1]:
				#	self.active[1].input(' ')
			elif symbol == key.BACKSPACE:
				#if self.active[1]:
				#	self.active[1].input('\b')
				pass
			elif symbol == key.TAB:
				if self.active[1] and hasattr(self.active[1], 'next'):
					self.active[1].next()
			elif symbol == key.ENTER:
				pass
				#self.active = None, None
			elif symbol == key.F11:
				pass #window.set_fullscreen(not window.fullscreen)
			else:
				if self.active[1]:
					try:
						if self.modifiers['shift']:
							pass#self.active[1].input(chr(symbol).upper())
						else:
							pass#self.active[1].input(chr(symbol))
					except:
						pass

	def draw_line(self, xy, dxy, color=(0.2, 0.2, 0.2, 1)):
		glColor4f(*color)
		glBegin(GL_LINES)
		glVertex2f(xy[0], xy[1])
		glVertex2f(dxy[0], dxy[1])
		glEnd()

	def render(self):
		self.clear()
		self.bg.draw()

		# for group_name in self.lines:
		# 	if group_name == 'link':
		# 		xy = self.lines[group_name][0]
		# 		dxy = self.lines[group_name][1]
		# 	elif type(self.lines[group_name]) == tuple:
		# 		try:
		# 			xy, dxy, color = self.lines[group_name]
		# 		except:
		# 			xy, dxy = self.lines[group_name]
		# 			color = colorConverter(255,255,255)
		# 	else:
		# 		xy = self.lines[group_name][0].x+self.lines[group_name][0].width/2, self.lines[group_name][0].y+self.lines[group_name][0].height/2
		# 		dxy = self.lines[group_name][1].x+self.lines[group_name][1].width/2, self.lines[group_name][1].y+self.lines[group_name][1].height/2

		# 	self.draw_line(xy, dxy, color)

		if len(self.mergeMap) > 0:
			merge_sprite = self.mergeMap.popitem()
			#if merge_sprite[0] == 'input':
			#	self.requested_input = merge_sprite[1][0]
			#	self.sprites[merge_sprite[0]] = merge_sprite[1][1]
			#else:
			self.sprites[merge_sprite[0]] = merge_sprite[1]

		for sprite_name, sprite in self.sprites.items():
			if sprite and sprite_name not in (None, 'line', 'etc..'):
				sprite._draw()

		if self.multiselect != False:
			for sprite_name in self.multiselect:
				sprite = self.sprites[sprite_name]
				sprite.draw_border(color=(0.2, 1.0, 0.2, 0.5))

		# if 'menu' in self.sprites:
		# 	self.sprites['menu']._draw()

		# if 'input' in self.sprites:
		# 	self.sprites['input']._draw()

		self.flip()

	def run(self):
		while self.alive == 1:
			self.render()

			# -----------> This is key <----------
			# This is what replaces pyglet.app.run()
			# but is required for the GUI to not freeze
			#
			event = self.dispatch_events()

nodesui = main()
if __name__ == '__main__':
	nodesui.run()