import pyglet
import math				# math.pi
from time import time			# Benchmark

objects = []
window = pyglet.window.Window(1500, 800, resizable = True)

def pixels_to_vertexlist(pixels):
	vertex_pixels = []
	vertex_colors = []

	for pixel in pixels:
		vertex = list(pixel)
		vertex_pixels += vertex[:-1]
		vertex_colors += list(vertex[-1])

	return pyglet.graphics.vertex_list(len(pixels), ('v2i', tuple(vertex_pixels)), ('c3B', tuple(vertex_colors)))

def gen_polygon(x = 300, y = 300, radius = 100, c = (255,0,0), base_rotation = 0, corners = 4):
	alpha = 2*math.pi/corners

	result = []
	for i in range(corners):
		corner_alpha = (i * alpha + base_rotation) % (2*math.pi)

		corner_x = int(math.cos(corner_alpha) * radius) + x
		corner_y = int(math.sin(corner_alpha) * radius) + y

		result += [(corner_x, corner_y, c)]

	return result

def draw():
	global objects, window, bg

	window.clear()

	# Update background
	pixels_to_vertexlist(bg).draw(pyglet.gl.GL_POLYGON)

	for o in objects:
		pixels_to_vertexlist(o).draw(pyglet.gl.GL_POLYGON)

def gen_bg(color=(0,0,0)):
	global window

	return gen_polygon(window.width>>1, window.height>>1, window.width>>1, color)

@window.event
def on_draw():
	draw()

@window.event
def on_resize(width, height):
	draw()

def gen_mess(num_objects, min_size = 20, max_size = 100):
	global window

	from random import randint

	# Valid positions
	margin = max_size // 2
	min_x = margin
	max_x = window.width - margin
	min_y = margin
	max_y = window.height - margin

	def rand_pos():
		return (randint(min_x, max_x),
			randint(min_y, max_y))

	def rand_radius():
		return randint(min_size, max_size)

	def rand_color():
		return (randint(0, 255),
			randint(0, 255),
			randint(0, 255))

	def rand_rotation():
		return randint(0, int(1000*math.pi)//2)/1000

	def rand_corners():
		return randint(3, 10)

	for o in range(num_objects):
		x, y = rand_pos()
		yield gen_polygon(x, y, rand_radius(), rand_color(), rand_rotation(), rand_corners())

bg = gen_bg((0,0,0))

for o in gen_mess(100):
	objects += [o]

t1 = time()
circle = gen_polygon(c = (255,150, 150), corners=25)
t2 = time()
print("Benchmark: circle took " + str(t2 - t1) + " seconds to generate.")

objects += [circle]

pyglet.app.run()
