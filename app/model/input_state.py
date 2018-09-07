import numpy as np

def build_input_state(game):
	index = 0
	player_turn = game.whose_turn()
	input_state = np.zeros((34, game.board.height, game.board.width), dtype=np.int)

	for board in reversed(game.boards[-8:]):
		board_state = build_board_state(board, player_turn)

		input_state[index] = board_state[0]
		input_state[index + 8] = board_state[1]
		input_state[index + 16] = board_state[2]
		input_state[index + 24] = board_state[3]

		index += 1

	input_state[32] = build_player_state(game.board, player_turn)
	input_state[33] = build_move_state(game.board, len(game.moves))

	return input_state

def build_board_state(board, player_turn):
	board_state = np.zeros((4, board.height, board.width), dtype=np.int)

	for row in range(board.height):

		translated_row = translate_row(row, board.height, player_turn);

		for column in range(board.width):
			translated_column = translate_column(column, board.width, player_turn);
			position = board.position_layout[row][column]
			piece = board.searcher.get_piece_by_position(position)

			if (piece):
				plane = 0 if player_turn == piece.player else 2
				plane += 1 if piece.king else 0;
				board_state[plane][translated_row][translated_column] = 1

	return board_state

def build_player_state(board, player_turn):
	if (player_turn == 1):
		return np.zeros((board.height, board.width), dtype=np.int)

	return np.ones((board.height, board.width), dtype=np.int)

def build_move_state(board, move_count):
	move_state = convert_to_binary_array(move_count, board.height * board.width)

	return np.reshape(move_state, (board.height, board.width))

def convert_to_binary_array(int_value, array_length):
	binary = "{0:b}".format(int_value).zfill(array_length)
	string_array = list(binary)
	return list(map(int, string_array))

def translate_row(row, board_height, player_turn):
	return board_height - 1 - row if player_turn == 1 else row;

def translate_column(column, board_width, player_turn):
	return board_width - 1 - column if player_turn == 1 else column;