#!/usr/bin/env python3
from json import loads, dumps
from collections import OrderedDict as OD

class node():
	def __init__(self, meta, x, y, scale=1.0):
		self.x = x
		self.y = y
		self.scale = scale
		self.meta = meta

class nodes():
	def __init__(self, inputData, width=800, height=600):
		self.width = width
		self.height = height

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

	def add(self, uniqueue_id, meta):
		if uniqueue_id in self.nodes:
			raise KeyError('Uniqueue ID \'' + str(uniqueue_id) + '\' already defined.')
		
		self.nodes[uniqueue_id] = node(meta)

		new_linkmap = []
		if 'links' in meta:
			for link in meta['links']:
				if not link in self.nodes:
					self.add(link, {'links' : [self.nodes[uniqueue_id]]})
				new_linkmap.append(self.nodes[link])
		self.nodes[uniqueue_id].meta['links'] = new_linkmap

	def parse(self):
		for key, meta in self.inputData.items():
			self.add(key, meta)