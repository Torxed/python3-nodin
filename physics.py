from math import sin, cos, asin, pi

class physics():
	def __init__(self):
		self.max_speed = 5					# Maximum speed for a fast node
		self.min_speed = 0.1				# Minimum speed before stopping the node
		self.friction_scale = -0.01			# Reduces acceleration with 1% per update

		self.link_attraction_scale = 1		# How much a link attracts a node
		self.node_repulsion_scale = 1		# How much nodes attract each other

		self.acceleration_scale = (1, 1)	# Should be defined according to width-height ratio

		self.velocities = {}

	def apply_friction(self, vector):
		"""Slows down a node's velocity-vector due to friction."""

		friction_vector = self.scale_vector(vector, friction_scale)
		return self.add_vectors(vector, friction_vector)

	def pythagoras(self, node1, node2):
		"""Calculates the distance between two objects in 2D-space."""

		# TODO: Optimize this code depending on what "nodes" looks like

		x_1 = x_2 = y_1 = y_2 = None
		if type(node1) == int or type(node1) == float:
			x_1, y_1 = 0, 0
			x_2, y_2 = node1, node2
		elif type(node1) == tuple:
			x_1, y_1 = node1
			x_2, y_2 = node2
		else:
			if node1.position and type(node1.position) == tuple:
				node1 = node1.position
				node2 = node2.position
			elif type(node1.x) == int:
				x_1, y_1 = node1.x, node1.y
				x_2, y_2 = node2.x, node2.y
			x_1, y_1 = node1
			x_2, y_2 = node2

		return ((x_2 - x_1)**2 + (y_2 - y_1)**2)**0.5

	def gen_vector(self, pos_1, pos_2):
		"""Creates a vector from position 1 to position 2."""

		x_1, y_1 = pos_1
		x_2, y_2 = pos_2

		angle = (y_2 - y_1) / (x_2 - x_1)
		speed = self.pythagoras(pos_1, pos_2)

		return (angle, speed)

	def add_vectors(self, vector_1, vector_2):
		"""Add vector_1 and vector_2 to each other."""

		angle_1, speed_1 = vector_1
		angle_2, speed_2 = vector_2

		# Convert the two vectors to (x,y) representation
		x_1 = cos(angle_1)*speed_1
		y_1 = sin(angle_1)*speed_1
		x_2 = cos(angle_2)*speed_2
		y_2 = sin(angle_2)*speed_2

		# Add the two vectors to each other
		x_result = x_1 + x_2
		y_result = y_1 + y_2

		# Convert the (x,y) of the result into (angle, speed)
		angle_result = asin(y_result)
		speed_result = self.pythagoras(x_result, y_result)

	def scale_vector(self, vector, scale):
		"""Scales the given vector. If scale==2, the vector becomes twice as
		long. If scale==0.5, the vector becomes half as long. If scale==-1,
		the vector is as long but becomes inverted (180 degrees)."""

		angle, speed = vector
		speed *= scale
		return (angle, speed)

	def accelerate(self, current_speed, acceleration_vector):
		"""Accelerates or (if vector is in the opposite direction of the
		current velocity) decelerates the given current speed."""

		acceleration_angle, acceleration_strength = acceleration_vector

		x, y = current_speed

		x += cos(acceleration_angle) * self.acceleration_scale[0] * acceleration_strength
		y += sin(acceleration_angle) * self.acceleration_scale[1] * acceleration_strength

		# TODO: Is it a good idea to round these down? It should eliminate all tiny
		#	movements, but perhaps small movements are needed for smoothness?
		x = int(x)
		y = int(y)

		return (x, y)

	def compute_forces(self, node):
		"""Computes the forces acting upon the nodes."""

		## Node is the NEIGHBOUR, self == node object.

		vectors = []
		#for neighbor in node.meta['links']:
		relation = self.gen_vector((self.x, self.y), (node.x, node.y))

		attr = self.scale_vector(relation, self.link_attraction_scale)
		rep = self.scale_vector(relation, self.node_repulsion_scale)

		vectors += [attr]
		vectors += [rep]

		# Compute the sum of all forces acting upon this node
		sum_vector = (0,0)
		for vector in vectors:
			sum_vector = self.add_vectors(sum_vector, vector)  ## == Fix: return value

		sum_vector = self.apply_friction(sum_vector)

		# TODO: Perform this comparison directly on sum_vector
		#	possibly before friction has been applied.
		old_velocity = node.velocity
		self.velocity = self.accelerate(velocities[node], sum_vector)

		# TODO: Don't go below min_speed
