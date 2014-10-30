## == In-house stuff:
from nodeui import nodesui
from node import nodes

tests = {}
tests['Anton Hvornum'] = {'links' : ['John Thilen', 'Serenity Mayflower']}

people = nodes(tests)
print(people.nodes)