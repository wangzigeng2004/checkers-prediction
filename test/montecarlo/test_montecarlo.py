import unittest
from random import randint
from functools import reduce
from app.montecarlo.node import Node
from app.montecarlo.montecarlo import MonteCarlo

class test_montecarlo(unittest.TestCase):

	def test_choice_is_correct(self):
		montecarlo = MonteCarlo(Node(0))
		montecarlo.child_finder = self.child_finder
		montecarlo.node_evaluator = self.node_evaluator

		for i in range(50):
			montecarlo.simulate()

		chosen_node = montecarlo.make_choice()
		self.assertIs(chosen_node.state, 1)

	def child_finder(self, node):
		if node.state == 0:
			node.add_children([Node(1), Node(-1)])
		else:
			for i in range(2):
				modifier = (100 if i == 1 else 200) * (-1 if node.state < 0 else 1)
				node.add_child(Node(node.state + modifier))

	def node_evaluator(self, node):
		if node.state > 1000:
			return 1
		elif node.state < -1000:
			return -1