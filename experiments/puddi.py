# Speed		How fast something moves (e.g. 5 pixels per frame)
#
# Velocity	How fast it moves, in a _specific_direction_ (e.g. 4 pixels per frame along a 29 degree angle)
#
# Vector	An arrow, that has an angle and a length. If the vector represents velocity, the length is the speed.

import math			# cos, sin, asin, pi
from time import sleep		# For the main loop

max_speed = 5			# Maximum speed for a fast node
min_speed = 0.1			# Minimum speed before stopping the node
friction_scale = -0.01		# Reduces acceleration with 1% per update

link_attraction_scale = 1	# How much a link attracts a node
node_repulsion_scale = 1	# How much nodes attract each other

acceleration_scale = (1, 1)	# Should be defined according to width-height ratio

# Global links
links = []			# (node1, node2)

nodes = {
	node : {		# node_id : {...}
		pos : (0,0),
		links : {}	# relation : node_id
	}
}

velocities = {}			# node_id : (x_speed, y_speed)		both can be positive or negative

def apply_friction(vector):
	"""Slows down a node's velocity-vector due to friction"""

	friction_vector = scale_vector(vector, friction_scale)
	return add_vectors(vector, friction_vector)

def pythagoras(node1, node2):
	"""Calculates the distance between two objects in 2D-space."""

	# TODO: Optimize this code depending on what "nodes" looks like
	x_1 = x_2 = y_1 = y_2 = None
	if type(node1) != tuple:
		if node1.position and type(node1.position) == tuple:
			node1 = node1.position
			node2 = node2.position
		elif type(node1.x) == int:
			x_1, y_1 = node1.x, node1.y
			x_2, y_2 = node2.x, node2.y

	x_1, y_1 = node1
	x_2, y_2 = node2

	return ((x_1 + x_2)**2 + (y_1 + y_2)**2)**0.5

def gen_vector(pos_1, pos_2):
	"""Creates a vector from position 1 to position 2."""

	x_1, y_1 = pos_1
	x_2, y_2 = pos_2

	angle = (y_2 - y_1) / (x_2 - x_1)
	speed = pythagoras(pos_1, pos_2)

	return (angle, speed)

def add_vectors(vector_1, vector_2):
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
	speed_result = (x_result**2 + y_result**2)**0.5		# Pythagoras

def scale_vector(vector, scale):
	"""Scales the given vector. If scale==2, the vector becomes twice as
	long. If scale==0.5, the vector becomes half as long. If scale==-1,
	the vector is as long but becomes inverted (180 degrees)."""

	angle, speed = vector
	speed *= scale
	return (angle, speed)

def accelerate(current_speed, acceleration_vector):
	"""Accelerates or (if vector is in the opposite direction of the
	current velocity) decelerates the given current speed."""

	acceleration_angle, acceleration_strength = acceleration_vector

	x, y = current_speed

	x += math.cos(acceleration_angle) * acceleration_scale[0] * acceleration_strength
	y += math.sin(acceleration_angle) * acceleration_scale[1] * acceleration_strength

	# TODO: Is it a good idea to round these down? It should eliminate all tiny
	#	movements, but perhaps small movements are needed for smoothness?
	x = int(x)
	y = int(y)

	return (x, y)

def compute_forces(nodes):
	"""Computes the forces acting upon the nodes."""

	# First run. Populate it.
	#
	# TODO: Optimize. Do not perform this check every single run
	if velocities == {}:
		for node in nodes:
			velocities[node] = (0,0)	# x and y speeds

	changed = False
	for node in nodes:
		vectors = []
		for link in node["links"]:
			neighbor = links[link]

			relation = gen_vector(node, neighbor)

			attr = scale_vector(relation, link_attraction_scale)
			rep = scale_vector(relation, node_repulsion_scale)

			#if too close:
			#	vector =
			#elif too far:
			#	attract

			vectors += [attr]
			vectors += [rep]

		# Compute the sum of all forces acting upon this node
		sum_vector = (0,0)
		for vector in vectors:
			sum_vector = add_vectors(sum_vector, vector)

		sum_vector = apply_friction(sum_vector)

		# TODO: Perform this comparison directly on sum_vector
		#	possibly before friction has been applied.
		old_velocity = velocities[node]
		new_velocity = accelerate(velocities[node], sum_vector)

		# TODO: Don't go below min_speed

		if old_velocity != new_velocity:
			changed = True

		# update velocity for this node
		velocities[node] = accelerate(velocities[node], sum_vector)

	# TODO: This is not always the same as everything standing still
	return changed		

def draw():
	global nodes

	# TODO: Graphics don't yet exist
	#window.clear()

	# Compute forces, which populates the velocities-list
	compute_forces(nodes)

	# Draw links
	for src,dst in links:
		src_pos = nodes[src]["pos"]
		dst_pos = nodes[dst]["pos"]

		draw_line(src_pos, dst_pos, color=..., arrow = True)

	# Draw nodes, including their text labels
	for node in nodes:
		x = node["position_x"]
		y = node["position_y"]

		text = node["text"]

		pixels_to_vertexlist(gen_circle(x, y, radius = text.width + 10, color = ...)).draw()

		gen_text(x, y, text, color = ...).draw()

	# Update positions based on current velocity. The new
	# positions will be used during the next iteration.
	for node in nodes:
		velocity_x, velocity_y = velocities[node]
		node_x, node_y = nodes[node]["pos"]

		# WARNING: Do not show this to a physiscist.
		node_x += velocity_x
		node_y += velocity_y

		nodes[node]["pos"] = (node_x, node_y)

# Populate global links with node data
for node in nodes:
	for link in node["links"]:
		links += [(node, node["links"][link])]

# Main loop
while compute_forces(nodes):
	# TODO: Handle input from user
	sleep(0.1)
	draw()
else:
	# TODO: Resume normal work
	pass
