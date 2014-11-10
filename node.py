#!/usr/bin/env python3
import math
from json import loads, dumps
from collections import OrderedDict as OD
from time import time

from physics import physics
#class physics():
#	pass

class node(physics):
	def __init__(self, meta, UID, scale=1.0):
		physics.__init__(self)
		self.x = meta['x']
		self.y = meta['y']
		self.velocity = (0, 0)

		self.UID = UID
		self.scale = scale
		self.meta = meta

		self.last_move = time()

	def update_children(self, x, y):
		for link in self.meta['links']:
			if hasattr(link, 'compute_forces'):
				if time() - link.last_move > 0.25:
					## JOHN:
					## This function will loop through direct neighbours only
					## and compute forces
					nx, ny = self.compute_forces(link)
					link.move(nx, ny)
			else:
				print('Child is missing physics, moving instant!')
				link.x += x
				link.y += y

	def move(self, x, y):
		diff = x-self.x, y-self.y
		self.x, self.y = x, y
		self.meta['x'] = self.x
		self.meta['y'] = self.y

		self.last_move = time()
		self.update_children(diff[0], diff[1])

class nodes():
	def __init__(self, inputData, width=800, height=600):
		self.width = width
		self.height = height
		self.center = int(width/2), int(height/2)

		if type(inputData) == str:
			self.inputData = loads(inputData)
			if not type(self.inputData) == dict: raise ValueError('Input data to nodes is not of type dict.')
		elif type(inputData) == bytes:
			self.inputData = loads(inputData.decode('utf-8'))
			if not type(self.inputData) == dict: raise ValueError('Input data to nodes is not of type dict.')
		elif type(inputData) == dict:
			self.inputData = inputData
		else:
			raise ValueError('Input data to nodes is not of type dict.')

		self.nodes = OD()
		self.parse()

	def fit_obj_around_path(self, objWidth, distance):
		return int((distance*2*math.pi)/objWidth)

	def angle_per_slize(self, numOfObjects):
		return int(360 / numOfObjects)

	def radiator(self, angle):
		return angle*(math.pi/180)

	def new_xy_space(self, x, y, angle, distance):
		newX = (math.cos(self.radiator(angle))*distance)+x
		newY = (math.sin(self.radiator(angle))*distance)+y
		return (newX, newY)

	def recalculate_space(self, obj):
		links = None

		if hasattr(obj, 'links'):
			links = obj.links
		elif 'links' in obj:
			links = obj['links']
		else:
			raise KeyError('Missing "links" object to recalculate space between children.')

		return self.angle_per_slize(len(links))

	def add(self, uniqueue_id, meta):
		if uniqueue_id in self.nodes:
			raise KeyError('Uniqueue ID \'' + str(uniqueue_id) + '\' already defined.')

		self.nodes[uniqueue_id] = node(meta, uniqueue_id)

		new_linkmap = []
		if 'links' in meta:
			for link in meta['links']:
				if not link in self.nodes:
					print('	Creating subnode:',link)
					self.add(link, {'links' : [uniqueue_id], 'x' : meta['x'], 'y' : meta['x']})
				new_linkmap.append(self.nodes[link])

		self.nodes[uniqueue_id].meta['links'] = new_linkmap

	def parse(self):
		objects_around_point = self.fit_obj_around_path(10, 40*len(self.inputData))

		for key, meta in self.inputData.items():
			if objects_around_point == 0:
				if not 'x' in meta:
					meta['x'] = self.center[0]
				if not 'y' in meta:
					meta['y'] = self.center[1]
			elif not 'x' in meta or not 'y' in meta:
				meta['x'], meta['y'] = self.new_xy_space(self.center[0], self.center[1], objects_around_point, len(self.inputData))

			print('Creating main object:',key)
			meta['color'] = '#FF0000'
			self.add(key, meta)

			if 'links' in meta:
				angleModifier = self.recalculate_space(self.nodes[key].meta)
				sliceID = 0
				for obj in self.nodes[key].meta['links']:
					obj.x, obj.y = self.new_xy_space(meta['x'], meta['y'], angleModifier*sliceID, 100)
					sliceID += 1
