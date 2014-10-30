#!/usr/bin/env python3
import math
from json import loads, dumps
from collections import OrderedDict as OD

class node():
	def __init__(self, meta, scale=1.0):
		self.x = meta['x']
		self.y = meta['y']
		self.scale = scale
		self.meta = meta

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

	def new_xy_space(self, x, y, angle, distance):
		newX = x + (math.cos(angle)*distance)
		newY = y + (math.sin(angle)*distance)
		return (newX, newY)

	def add(self, uniqueue_id, meta):
		if uniqueue_id in self.nodes:
			raise KeyError('Uniqueue ID \'' + str(uniqueue_id) + '\' already defined.')
		
		self.nodes[uniqueue_id] = node(meta)

		new_linkmap = []
		if 'links' in meta:
			objects_around_point = self.fit_obj_around_path(10, 40*len(meta['links']))
			a = self.angle_per_slize(objects_around_point)
			sliceID = 0
			for link in meta['links']:
				if not link in self.nodes:
					print('	Link:',link)
					x, y = self.new_xy_space(self.nodes[uniqueue_id].x, self.nodes[uniqueue_id].y, a*sliceID, 10*len(meta['links']))
					self.add(link, {'links' : [uniqueue_id], 'x' : x, 'y' : y})
				new_linkmap.append(self.nodes[link])
				sliceID += 1
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