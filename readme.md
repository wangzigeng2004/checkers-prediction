A Python Flask app that uses unsupervised learning to train a neural network to learn how to play checkers (aka draughts).

There are two endpoints: `/train` and `/predict`. These can be used to retrain the AI and predict the best move for a given board state. If no training has yet occurred, the AI will predict a random move.

This was built to work in conjunction with the [web app](https://github.com/ImparaAI/checkers-web) and can easily be run in a Kubernetes cluster as defined [here](https://github.com/ImparaAI/checkers-kubernetes).

# Routes

## /train
Method: `POST`

Input: `episodes=int, time_limit_in_seconds=int`

## /predict
Method: `GET`

Input: `moves=[[int, int], [int, int], ...]`

Output: `[int, int]`

# Assumptions

The rules used are for competitive American checkers or English draughts. This means an 8x8 board with force captures and regular kings.

Each position on the board is numbered 1 to 32. Each move is represented as an array with two values: starting position and ending position. So if you're starting a new game, one of the available moves is `[9, 13]` for player 1. If there's a capture move, the ending position is the position the capturing piece will land on (i.e. two rows from its original row), which might look like `[13, 22]`.

Each piece movement is completely distinct, even if the move is part of a multiple capture series. In [Portable Draughts Notation](https://en.wikipedia.org/wiki/Portable_Draughts_Notation) mutli-capture series are usually represented by a `5-32` (for a particularly long series of jumps), but in certain situations there could be multiple pathways to achieve that final position. This app requires an explicit spelling out of each distinct move in the multi-capture series. The app will understand when it's still a player's turn because it's mid-multi-capture.

# Training strategy

This app uses a Monte Carlo tree search that roughly follows the methods used by [AlphaGo Zero](https://www.nature.com/articles/nature24270.epdf?author_access_token=VJXbVjaSHxFoctQQ4p2k4tRgN0jAjWel9jnR3ZoTv0PVW4gB86EEpGqTRDtpIz-2rmo8-KG06gqVobU5NSCFeHILHcVFUeMsbvwS-lxjqQGg98faovwjxeTUgZAUMnRQ). In short, every time it's the AI's turn to move, it uses one neural net to reduce the number of moves it should consider and another to evaluate the expected value of any particular move as we traverse the tree of possible moves in future rounds. In Google's terminology these are called the "policy network" and the "value network" respectively.

Each training run starts the neural net over from scratch. By default, a training run lasts for 1000 games, but it's also possible to restrict this on time and number of games depending on the limitations of your machine.

## Neural network architecture

The neural net's job is to reduce the amount of digging for the Monte Carlo tree search algorithm. The network itself is structurally identical to the AlphaZero network with the exception of the inputs, the predicted outputs, and certain small details in the convolutional layers

### Input

The input to the neural net is a multidimensional numpy array that is `34 x 8 x 4` (depth x height x width), or `34` layers of `8 x 4` 2d arrays. The `8 x 4` is determined by the shape of the board. Ignoring the white spaces, each checkers board has 8 vertical spots and 4 horizontal spots. The `34` is made up like this:

- Layers **1-32** hold the state of the board's pieces for the last 8 moves. So layers **1-4** hold the board state for the most recent move, layers **5-8** hold the board state for the second most recent move, etc. Within a single move's board state, the first layer describes the position of the current player's non-king pieces, the second layer is for the current opponent's non-king pieces, the third is the current player's king pieces, and the fourth is the current opponent's king pieces. The distinction between the current player and the opponent is important as the neural net only ever makes predictions from the perspective of the current player.
- Layer **33** has all 0s if it's player 1's turn and all 1s if it's player 2's turn.
- Layer **34** has a binary representation of the current move count. If it's move 29, that would be represented as `11101` in binary. That is then converted into a numpy `8 x 4` array that looks like `[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [1, 1, 0, 1]]`.

The end result is that every value in this multidimensional input is either a `1` or a `0` and it fully represents everything about the current state of the board and the 7 previous moves.

### Outputs

The neural net has two outputs:

- A float that represents the expected win value for the current player given the current board state. In the Monte Carlo tree search algorithm this is the `W` value for the node being evaluated.
- A flat list 256 elements long, each of which hold a float value between `0` and `1` representing a success probability for choosing that move. Each spot on the board gets 8 potential move positions representing the direction and the distance of the move. So positions `0-7` in this array are reserved for spot 1's potential moves:

- **0**: move 1 spot to the southeast
- **1**: move 1 spot to the southwest
- **2**: move 1 spot to the northeast
- **3**: move 1 spot to the northwest
- **4**: move 2 spots to the southeast
- **5**: move 2 spots to the southwest
- **6**: move 2 spots to the northeast
- **7**: move 2 spots to the northwest

This is repeated for all 32 positions on the board, for a total of 256 elements. During training, the output values are simply `0`s and `1`s, but predictions provide a probability of success between `0` and `1`. When the Monte Carlo tree search is making decisions about which moves to populate as child nodes, it iterates over all possible moves and finds the probability values (`p`) for them from this output, which eliminates the need to drill down further for that child node as you might do in a non-NN MCTS algorithm.

### Differences with AlphaZero

By default, this app uses 75 convolution kernels (i.e. "neurons") per convolutional layer whereas AlphaZero uses 256. AlphaZero also uses 40 residual layers where this app uses 6. The reasons for this are:

- Checkers is inherently simpler than Chess or Go
- We expect training to work decently on a moderately powerful CPU, rather than necessarily on a GPU or TPU

It's worth keeping in mind that in neural nets finding the right number of "neurons" and residual layers is a bit of an art. There may indeed be a way of precisely quantifying the correlation between prediction accuracy and these hyperparameters for specific problems, but when this app was made it was not immediately obvious to us how to do it. Our method for choosing these numbers was a process of trial and error with a goal of minimizing them (for performance) while subjectively keeping a high enough prediction accuracy.

# Why checkers?

Since checkers is a much simpler game than go or chess, the solution space is drastically reduced, while not being so trivial that it can be easily brute-forced on a regular computer in a short amount of time (like tic-tac-toe). This app's training can be run on a relatively cheap machine and doesn't really require a GPU or TPU.

# Testing

Go to the app directory and run `python3 -m unittest discover` or just `test` if you're in the Docker container.