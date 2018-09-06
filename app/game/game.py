from .board import Board

class Game(object):

	def __init__(self):
		self.board = Board()
		self.boards = [self.board];
		self.moves = []
		self.move_limit = 500

	def move(self, move):
		if move not in self.get_possible_moves():
			raise ValueError('The provided move is not possible')

		self.board = self.board.create_new_board_from_move(move)
		self.boards.append(self.board)
		self.moves.append(move)

		return self

	def move_limit_reached(self):
		return len(self.moves) >= self.move_limit

	def is_over(self):
		return self.move_limit_reached() or not self.get_possible_moves()

	def get_winner(self):
		if not self.board.count_movable_player_pieces(1):
			return 2
		elif not self.board.count_movable_player_pieces(2):
			return 1
		else:
			return None

	def get_possible_moves(self):
		return self.board.get_possible_moves()

	def whose_turn(self):
		return self.board.player_turn