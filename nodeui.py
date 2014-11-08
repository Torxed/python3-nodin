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
	r = r/255.0
	g = g/255.0
	b = b/255.0
	a = a/255.0
	return r,g,b,a

def mainThread():
	""" Returns (none or) a handle to the main "thread" object. """ 
	for t in enumerate():
		if t.name == 'MainThread':
			return t
	return None

def positionals(args, keys, defaults=None, _map_ = {}):
	if len(args) > len(keys):
		raise TypeError('Positional arguments surpasses length of arguments to take in.')
	for i in range(len(keys)):
		if keys[i] in _map_:
			continue
		#	raise KeyError('Positional argument overwriting dictorial argument: ' + str(keys[i]))
		elif len(args) < i and len(args) > 0:
			_map_[keys[i]] = args[i]
		else:
			if defaults is not None:
				_map_[keys[i]] = defaults[keys[i]] 
			else:
				_map_[keys[i]] = None
	return _map_

class GenericObject(pyglet.sprite.Sprite):
	def __init__(*args, **dictWars):
		"""
		Bugs found:
			- if no texture is given, trying to call move() will end up in a error stating _x is not defined
		"""

		## == If we are inherited from another class,
		##    the arguments will be passed only into *args and we
		##    need to unpack them outselves if 4 conditions are met
		##    that can only happen if we are inherited.
		## :: This ensures us to be fully dynamic against classes
		##    interested in inheriting from us.
		##    It means that you can pass whatever arguments you want
		##    into this generic object and access them from your
		##    own class, we don't force you to any positional
		##    or optional parameters. There are some basic parameters
		##    that are required by the graphical system tho but we'll
		##    set them if not set to some defaults.
		if type(args) == tuple and len(args) == 2 and len(dictWars) == 0 and type(args[1]) == dict:
			args, dictWars = args
		self = args[0]		


		## == TODO: Preferably the arguments themselves should be None across all
		## ==       variables instead of setting them to False, None, 0 etc.
		## ==       And it's up to each individual function to recognize a None value
		## ==       and replace it with what it needs locally?
		m = {'texture' : None, 'width' : None, 'height' : None, 'color' : '#C2C2C2', 'x' : 0, 'y' : 0, 'anchor' : 'center', 'scale' : 1.0}
		dictWars = positionals(args[1:], ['texture', 'width', 'height', 'color', 'x', 'y', 'anchor', 'scale'], defaults=m, _map_=dictWars)

		self.render = True
		self.moveable = True
		self.moving = True

		if dictWars['texture'] and isfile(dictWars['texture']):
			self.texture = pyglet.image.load(dictWars['texture'])
		else:
			## If no texture was supplied, we will create one
			if dictWars['width'] is None:
				dictWars['width'] = 10
			if dictWars['height'] is None:
				dictWars['height'] = 10
			self.texture = self.gen_solid_img(dictWars['width'], dictWars['height'], dictWars['color'], alpha=255)

		## We must instanciate pyglet.sprite.Sprite before
		## doing anything else because otherwise x, y, scale etc
		## will be overwritten or not accessible in Python3.
		## (Python2 would work fine as long as supplied as an inheritance)
		super(GenericObject, self).__init__(self.texture)
		
		self.scale = dictWars['scale']
		if dictWars['width'] and dictWars['width'] < self.texture.width:
			self.scale = (1.0/max(dictWars['width'], self.texture.width))*min(dictWars['width'], self.texture.width)
		elif dictWars['height'] and dictWars['height'] < self.texture.height:
			tmp = (1.0/max(dictWars['height'], self.texture.height))*min(dictWars['height'], self.texture.height)
			if tmp > self.scale:
				self.scale = tmp
			#else:
			#	Already scaled below needed threshold

		self.anchor = dictWars['anchor']
		if self.anchor == 'center':
			self.image.anchor_x = self.image.width / 2
			self.image.anchor_y = self.image.height / 2

		self.x = dictWars['x']
		self.y = dictWars['y']

		self.triggers = {'hover' : False}
		self.colorcode = dictWars['color']

		self.dictWars = dictWars

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

	def color_converter(self, c, alpha=255):
		if c[0] == '#':
			c = c.lstrip("#")
			c = max(6-len(c),0)*"0" + c
			r = int(c[:2], 16)
			g = int(c[2:4], 16)
			b = int(c[4:], 16)
			c = (r,g,b,alpha)#int(0.2*255))
		return c

	def gen_solid_img(self, width, height, c='#C2C2C2', alpha=255):
		return pyglet.image.SolidColorImagePattern(self.color_converter(c, alpha)).create_image(width,height)

	def draw_circle(self, x, y, radius, c='#FF0000', AA=60, rotation=0, stroke=False):
		glColor4f(*self.color_converter(c))
		glPushMatrix()

		glTranslatef(x, y, -0) # 0=z
		glRotatef(rotation, 0, 0, 0.1)

		if radius < 1 : radius = 1

		if stroke:
			inner = radius - stroke # outline width
			if inner < 0: inner=0
		else :
			 inner = 0 # filled

		q = gluNewQuadric()
		
		gluQuadricDrawStyle(q, GLU_FILL) #glu style
		gluDisk(q, inner, radius, AA, 1) # gluDisk(quad, inner, outer, slices, loops)
		
		glPopMatrix()

	def draw_line(self, to, c='#FF0000'):
		if type(to) == Node:
			xy, dxy = (self.x, self.y), (to.x, to.y)
		elif type(to) == tuple:
			xy, dxy = to
		else:
			return None

		glColor4f(*self.color_converter(c))#color[0], color[1], color[2], color[3])
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
		if self.anchor == 'center':
			if (self.x-(self.width/2)) < x < (self.x+(self.width/2)):
				if (self.y-(self.height/2)) < y < (self.y+(self.height/2)):
					return self
		else:
			if self.x < x < self.x+self.width:
				if self.y < y < self.y+self.height:
					return self

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

	def drag(self, x, y):
		self.move(x, y)

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

class Node(GenericObject):
	def __init__(*args, **dictWars):
		if type(args) == tuple and len(args) == 2 and len(dictWars) == 0 and type(args[1]) == dict:
			args, dictWars = args
		self = args[0]
		GenericObject.__init__(args, dictWars)

		self.sync_children = []
		self.updating_factor = 1.0

	#def update_children(self, x, y, factor=1.0):
	#	for link in self.dictWars['nodeObj'].links:
	#		if link in self.dictWars['sprites'] and self.dictWars['sprites'][link].moveable:
	#			self.dictWars['sprites'][link].move(x*factor, y*factor)

	def drag(self, x=0, y=0):
		pass

	def on_mouse_motion(self, x, y, dx, dy):
		print(x, y, dx, dy)
		if self.moving:
			## Update both object and graphics
			self.dictWars['nodeObj'].x = self.x = x+dx
			self.dictWars['nodeObj'].y = self.y = y+dy

	def move(self, x, y):
		#self.x += x*self.updating_factor
		#self.y += y*self.updating_factor
		#self.moveable = False
		#self.update_children(x, y, factor=self.updating_factor*0.8)
		#self.moveable = True
		pass

	def _draw(self):
		#self.moveable = False
		for link in self.dictWars['nodeObj'].links:
			if link in self.dictWars['sprites']:
				self.draw_line(self.dictWars['sprites'][link], c='#00000')
		#self.moveable = True
		self.draw_circle(self.dictWars['nodeObj'].x, self.dictWars['nodeObj'].y, 5, c=self.colorcode, AA=60, rotation=0, stroke=False)

class main(pyglet.window.Window):
	def __init__ (self,):
		super(main, self).__init__(800, 600, fullscreen = False, caption='Nodes')
		self.bg = GenericObject(width=800, height=600, color=(228,228,228,255), anchor='botleft')

		self.sprites = OD()
		#self.lines = OD()
		self.mergeMap = OD()
		
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
					if hasattr(sprite_obj, 'on_mouse_motion'):
						sprite_obj.on_mouse_motion(x, y, dx, dy)
					elif hasattr(sprite_obj, 'hover'):
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
			if self.active[1] and not self.moving and self.multiselect == False:
				self.active[1].click(x, y, self.mergeMap)
		elif button == 4:
			if not self.active[0]:
				pass #Do something on empty spaces?
			else:
				self.active[1].right_click(x, y, self.mergeMap)

		self.moving = False
	
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
		self.moving = True
		if self.active[1] and self.multiselect == False:
			if not hasattr(self.active[1], 'physics'):
				self.active[1].drag(dx, dy)
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

	def plot_nodes(self, nodemap):
		for key, node in nodemap.items():
			print('Plotting:',key,'(x={0}, y={1})'.format(node.x, node.y))
			color = (0,0,0,255)
			if 'color' in node.meta:
				color = node.meta['color']
			self.mergeMap[key] = Node(x=node.x, y=node.y, width=10, height=10, color=color, nodeObj=node, sprites=self.sprites)

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