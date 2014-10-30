## == In-house stuff:
from nodeui import nodesui
from node import nodes

tests = {}
tests['Anton Hvornum'] = {'links' : ['John Thilen', 'Serenity Mayflower', 'Nelly Söderlind', 'Elias Hvornum']}

people = nodes(tests)

nodesui.plot_nodes(people.nodes)
nodesui.run()