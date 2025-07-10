```
_________ .__                          
\_   ___ \|  |__   ____   ______ ______
/    \  \/|  |  \_/ __ \ /  ___//  ___/
\     \___|   Y  \  ___/ \___ \ \___ \ 
 \______  /___|  /\___  >____  >____  >
        \/     \/     \/     \/     \/ 
```

# Introduction
This project aims to explore all aspects related to the software development of a chess game. It will include the game engine, a graphical interface, a very simple bot implementation, and finally, the training of that bot.

# Game Engine
This chess engine is based on bitboards, and more specifically on magic bitboards. The bitboard representation is a square-based implementation that relies on the fact that a chessboard contains 64 squares. For each piece category, if we mark the presence of a piece on a square with a 1 and the absence with a 0, then it is possible to represent a type of piece using a 64-bit integer. If we do this for the 6 categories of pieces for each player, then with 12 64-bit integers, we can represent a chessboard. The advantages of this implementation are that it is very efficient in terms of calculation speed while also having an efficient memory representation. Indeed, the calculations are almost exclusively bitwise operations, which are very fast even in Python. The main drawback is debugging, because we are dealing with 64-bit integers, which are less readable compared to an 8x8 matrix.
Moreover, to speed up calculations even further, we use magic bitboards. Simply put, these are precomputed attack dictionaries. We input the position of the piece whose attack pattern we want to know and the positions of the opponent’s pieces, and we directly obtain the squares attacked by that piece.
Regarding the move system, we implemented our own version where a move is designated by "Piece.column.row-Piece.column.row(-special.move)" — for example, "Pe2-Pe4" instructs the pawn on e2 to move to e4, and "Ke1-Kg1-o" is the notation for castling. Here is the list of special notations: "\*" indicates en passant, a "number" indicates promotion to the designated piece, and "o" or "O" indicate O-O and O-O-O castling respectively. Almost all the game rules are implemented except the rule of the 3 repeated positions.
Currently, it is possible to load a game using the FEN notation.

# Game renderer
This part of the project is quite simple. It’s a basic implementation using Pygame that allows you to visualize the board and play. When you click on a piece, the list of its legal moves is displayed, and if you click on one of those squares, the move is played. It’s possible to plug in bots to play instead of one or both players. They just need to have a function called "make\_decision" that takes a board as input and returns a move according to the notation described above. However, the display of pawn promotions is still missing. Currently, a human player can only promote to a knight (which is not the case for a plugged-in bot).
You can set the bottom player with the bottom attributes and you can modify the canvas size with the size attributes.

# Chess bot
Our choice for implementing the chess bot is based on the concept from the YouTuber "Green Lemon Games," who builds chess bots using rules predefined by his chat, and whose bots can only look one move ahead. The goal was to create a bot capable of evaluating all its possible moves by considering the best possible reply from its opponent for each move, and then selecting what it believes to be the best move to play.
A lot of rules and more precise optimization for each parameter is needed for the bot to be considered a good opponent but for now it is able to put up a good fight.

# Bot training
For the bot training, we wanted an implementation where it plays against itself like AlphaZero, in order to optimize the different parameters that help it make decisions. The current implementation is quite rudimentary and consists only of a random selection of the best set of parameters, in a style similar to a genetic algorithm but without crossover or mutation.
What is trained is called a ChessParameters class which should contain a dictionnary of parameters for the bot to use and an attribute `score` to indicate its score during the evaluation.

# Futur implementation
Future improvements for this project include implementing the threefold repetition rule, which leads to a draw, and adding more comprehensive rules for the bot. We also plan to develop better training methods to optimize the bot’s performance. Enhancing support for international move notation is another priority, along with adding proper pawn promotion handling in the visual engine. We can also implement an evaluation bar using the score of the bot evaluation. There is a known bug related to the expression 1 << (index - 2) that needs fixing. Additionally, we want to enable undoing moves to allow players to go back after making a move. Finally, integrating the ability to play games on Chess.com is a longer-term goal. Indices are inverted meaning a1 != 0 and h3 != 63, therefore it needs to be fixed.