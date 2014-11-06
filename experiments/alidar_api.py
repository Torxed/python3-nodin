import fancy_gui
import storage_api import search, fetch, add

# TODO: Automate class generation.
class Person(Node):
	def __init__(self, name):
		# Find user in database
		result = storage_api.search(name, category="person", fields=["uid"])
		uid = None
		if not result:
			uid = storage_api.add("person", {"name" : name})
		else:
			uid = result[0]

		# Populate this node's data object
		self.data = {
			"uid" : uid,
			"name" : name,
			"friends" : set()
		}
		for friend_pair in storage_api.fetch("friends", uid):
			uid1 = friend_pair[0]["uid"]
			uid2 = friend_pair[1]["uid"]

			# Don't add ourselves as friends
			if uid == uid1:
				self.data["friends"].add(uid2)
			elif uid == uid2:
				self.data["friends"].add(uid1)

		# Which data values to use for what when rendering this node
		self.label = "name"
		
		# Which default-field to use in source code to reference
		# this particular node
		self.identity = "uid"

		# Override the default node color
		self.color = "#ABC123"

mowgli = Person("Mowgli")

for panther in fancy_gui.get(type="panther"):
	if panther["name"] == "Bagheera":
		if panthernot in mowgli["friends"]:
			mowgli["friends"].add(panther)
		panther["friends"].add(mowgli)
