# Import libraries
import chess, chess.engine, chess.pgn
from stockfish import Stockfish
# Import files
import vision, utility, display, tables, control

############# SETUP #############
stockfish = Stockfish()
print(stockfish.get_parameters())
print(stockfish.get_stockfish_major_version())
#################################

def new_board():
    # Create a new board
    board = chess.Board()

    return board

def start_display(board):
    # Start the display based of current state of the board
    display.start(board.fen())

    return display

def user_move(board, board_coords, board_frame, detection_graph, category_index, past_image, new_image):
    # Run detections on images
    past_detection = vision.run_detection(detection_graph, category_index, past_image)
    new_detection = vision.run_detection(detection_graph, category_index, new_image)
    vision.get_difference(past_image, new_image)

    # Set initial variables
    board_test = False
    loop_count = 0

    # Run loop to place board and re-run if failed
    while (board_test == False) and (loop_count < 3):
        past_mapped = utility.place_points(board_coords, past_detection)
        new_mapped = utility.place_points(board_coords, new_detection)
        board_test = utility.test_board(past_mapped, new_mapped)
        if board_test:
            past_detection = vision.run_detection(detection_graph, category_index, past_image)
            new_detection = vision.run_detection(detection_graph, category_index, new_image)
        loop_count = loop_count + 1

    # Get the move made
    user_move = utility.get_move(past_mapped, new_mapped)
    move = chess.Move.from_uci(user_move)

    # Test move is legal and push to board
    if board.legal_moves.__contains__(move):
        board.push(move)
        board_frame.move_piece(str(move))
        return True
    else:
        # Display appropriate error is illegal move
        if user_move == "0000":
            display.show_error()
        else:
            display.show_warning()
        return False

def computer_move(board, board_frame, comm):
    # Use stockfish library to perform computer move
    stockfish.set_fen_position(board.fen())
    print("Stockfish - Processing")
    result = stockfish.get_best_move()
    board.push_san(result)
    board_frame.move_piece(str(result))
    if display.is_take():
        control.take_move(comm, str(result))
    else:
        control.standard_move(comm, str(result))

def get_pieces(board):
    # Count pieces of each side and display on board
    white_count = 0
    black_count = 0
    for i in board.fen():
        if i not in [' ', '/']:
            if i.isupper():
                white_count = white_count + 1
            if i.islower():
                black_count = black_count + 1
        if i == ' ':
            break

    return white_count, black_count

def evaluate_board(board):
    # Set initial values
    evaluation = 0
    weightings = [100, 320, 330, 500, 900]

    # Calculate evalution
    for piece in range(1,7):
        # White
        piece_count_white = (len(board.pieces(piece, chess.WHITE)))
        piecesq_white = sum([tables.combined_table[piece-1][i] for i in board.pieces(piece, chess.WHITE)])

        # Black
        piece_count_black = (len(board.pieces(piece, chess.BLACK)))
        piecesq_black = sum([-tables.combined_table[piece-1][chess.square_mirror(i)] for i in board.pieces(piece, chess.BLACK)])

        # Board
        if piece != 6:
            material = weightings[piece-1]*(piece_count_white-piece_count_black)
        else:
            material = 0

        evaluation = evaluation + material + piecesq_white + piecesq_black

    # Return positive or negative depending on user move
    if board.turn:
        return evaluation
    else:
        return -evaluation

def configure(_skill, _hash):
    # Apply configuration requirements to engine
    stockfish = Stockfish(parameters={"Skill Level": _skill, "Hash": _hash})
    print(stockfish.get_parameters())
    print(stockfish.get_stockfish_major_version())
