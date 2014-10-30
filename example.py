## == In-house stuff:
from nodeui import nodesui
from node import nodes

tests = {}
tests['Anton'] = {'links' : ['John', 'Serenity']}

people = nodes(tests)
print(people.nodes)
