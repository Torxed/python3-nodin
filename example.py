## == In-house stuff:
from nodeui import nodesui
from node import nodes

tests = {}
tests['Torxed'] = {'links' : ['Alidar', 'Serenity']}

people = nodes(tests)
print(people.nodes)
