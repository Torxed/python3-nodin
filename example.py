## == In-house stuff:
from nodeui import nodesui
from node import nodes

tests = {}
tests['Anton Hvornum'] = {'links' : ['Baloo', 'Shere Khan', 'Apan som lagar', 'Vilde Ville', 'Mac Gyver']}

people = nodes(tests)

nodesui.plot_nodes(people.nodes)
nodesui.run()