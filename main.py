# Include libraries
import cv2, os, time
import tkinter as tk
import tensorflow as tf
from tkinter import ttk
from utils import label_map_util
# include files
import engine, display, control, vision

# Start video capture
capture = cv2.VideoCapture(0)

# Edited standard code from tensorflow model zoo
# Get the model
MODEL_NAME = 'new_graph'
MODEL_FILE = MODEL_NAME + '.tar.gz'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('data', 'object-detection.pbtxt')

# Set number of classes
NUM_CLASSES = 6

# Load a frozen Tensorflow model into memory to improve execution speed
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Open serial communication into a global variable and set arm to default position
comm = control.initialize()
control.reset_arm(comm)

# Wait for arm to move
time.sleep(6)

# Define variables globally
flags = [False, False, False]
past_ret, past_image = capture.read()
board_coords = vision.get_board(past_image)
past_ret, past_image = capture.read()

# Start running display
root, board_frame, play_frame = display.run()

def set_flags(flag):
    # Set flags globally
    global flags
    if flag == "playing_flag":
        flags[0] = True
    elif flag == "move_flag":
        flags[1] = True
    elif flag == "calibrate_flag":
        flags[2] = True

def start_func():
    # Function run when start game started
    global past_image
    past_ret, past_image = capture.read()
    play_frame.configure_white("White Pieces : 16")
    play_frame.configure_black("Black Pieces : 16")
    play_frame.configure_turn("Current Turn : USER (white)")
    play_frame.configure_evaluation("Evaluation : 0")
    set_flags("playing_flag")

def polling(board):
    # Main polling function
    global flags, past_image
    # Check playing flag
    if flags[0] == True:
        # If user turn
        if board.turn:
            # Check move flag
            if flags[1] == True:
                new_ret, new_image = capture.read()
                successful = engine.user_move(board, board_coords, board_frame, detection_graph, category_index, past_image, new_image)
                # Run if move successful
                if successful:
                    past_image = new_image
                    # Update info labels
                    play_frame.configure_turn("Current Turn : Computer (black)")
                    play_frame.configure_evaluation(("Evaluation : " + str(engine.evaluate_board(board))))
                    white_count, black_count = engine.get_pieces(board)
                    play_frame.configure_white(("White Pieces : " + str(white_count)))
                    play_frame.configure_black(("Black Pieces : " + str(black_count)))
                # Reset flag
                flags[1] = False
        # If computer turn
        else:
            # Get and apply computers move
            engine.computer_move(board, board_frame, comm)
            # Update info labels
            play_frame.configure_turn("Current Turn : USER (white)")
            play_frame.configure_evaluation(("Evaluation : " + str(engine.evaluate_board(board))))
            white_count, black_count = engine.get_pieces(board)
            play_frame.configure_white(("White Pieces : " + str(white_count)))
            play_frame.configure_black(("Black Pieces : " + str(black_count)))

    # Check calibrate flag
    if flags[2] == True:
        # Calibrate the board, note the board must be empty
        global board_coords
        board_coords = vision.get_board(past_image)
        flags[2] = False

    # Re-call polling function in 100ms
    root.after(100, lambda : polling(board))

# Auto-run main function
if __name__ == '__main__':
    # Define White Pieces
    WHITE_KING = tk.PhotoImage(file="pieces\KING_W.png")
    WHITE_QUEEN = tk.PhotoImage(file="pieces\QUEEN_W.png")
    WHITE_ROOK = tk.PhotoImage(file="pieces\ROOK_W.png")
    WHITE_KNIGHT = tk.PhotoImage(file="pieces\KNIGHT_W.png")
    WHITE_BISHOP = tk.PhotoImage(file="pieces\BISHOP_W.png")
    WHITE_PAWN = tk.PhotoImage(file="pieces\PAWN_W.png")

    # Define Black Pieces
    BLACK_KING = tk.PhotoImage(file="pieces\KING_B.png")
    BLACK_QUEEN = tk.PhotoImage(file="pieces\QUEEN_B.png")
    BLACK_ROOK = tk.PhotoImage(file="pieces\ROOK_B.png")
    BLACK_KNIGHT = tk.PhotoImage(file="pieces\KNIGHT_B.png")
    BLACK_BISHOP = tk.PhotoImage(file="pieces\BISHOP_B.png")
    BLACK_PAWN = tk.PhotoImage(file="pieces\PAWN_B.png")

    # Place White Pieces on Board
    board_frame.new_piece('W0', WHITE_ROOK, 0, 0)
    board_frame.new_piece('W1', WHITE_KNIGHT, 0, 1)
    board_frame.new_piece('W2', WHITE_BISHOP, 0, 2)
    board_frame.new_piece('W3', WHITE_QUEEN, 0, 3)
    board_frame.new_piece('W4', WHITE_KING, 0, 4)
    board_frame.new_piece('W5', WHITE_BISHOP, 0, 5)
    board_frame.new_piece('W6', WHITE_KNIGHT, 0, 6)
    board_frame.new_piece('W7', WHITE_ROOK, 0, 7)
    board_frame.new_piece('W8', WHITE_PAWN, 1, 0)
    board_frame.new_piece('W9', WHITE_PAWN, 1, 1)
    board_frame.new_piece('W10', WHITE_PAWN, 1, 2)
    board_frame.new_piece('W11', WHITE_PAWN, 1, 3)
    board_frame.new_piece('W12', WHITE_PAWN, 1, 4)
    board_frame.new_piece('W13', WHITE_PAWN, 1, 5)
    board_frame.new_piece('W14', WHITE_PAWN, 1, 6)
    board_frame.new_piece('W15', WHITE_PAWN, 1, 7)

    # Place Black Pieces on Board
    board_frame.new_piece('B0', BLACK_ROOK, 7, 0)
    board_frame.new_piece('B1', BLACK_KNIGHT, 7, 1)
    board_frame.new_piece('B2', BLACK_BISHOP, 7, 2)
    board_frame.new_piece('B3', BLACK_QUEEN, 7, 3)
    board_frame.new_piece('B4', BLACK_KING, 7, 4)
    board_frame.new_piece('B5', BLACK_BISHOP, 7, 5)
    board_frame.new_piece('B6', BLACK_KNIGHT, 7, 6)
    board_frame.new_piece('B7', BLACK_ROOK, 7, 7)
    board_frame.new_piece('B8', BLACK_PAWN, 6, 0)
    board_frame.new_piece('B9', BLACK_PAWN, 6, 1)
    board_frame.new_piece('B10', BLACK_PAWN, 6, 2)
    board_frame.new_piece('B11', BLACK_PAWN, 6, 3)
    board_frame.new_piece('B12', BLACK_PAWN, 6, 4)
    board_frame.new_piece('B13', BLACK_PAWN, 6, 5)
    board_frame.new_piece('B14', BLACK_PAWN, 6, 6)
    board_frame.new_piece('B15', BLACK_PAWN, 6, 7)

    # Add title label
    Title = ttk.Label(root, text="Chess",font=("Helvetica", 20))
    Title.place(x=560,y=10)

    #  Add play Game Buttons
    start_button = ttk.Button(root, text="Start Game", command= lambda: start_func())
    start_button.place(x=700, y=275)
    move_test = ttk.Button(root, text="Calibrate", command= lambda: set_flags("calibrate_flag"))
    move_test.place(x=415, y=275)
    completed_turn = ttk.Button(root, text="Finish Turn", command= lambda: set_flags("move_flag"))
    completed_turn.place(x=505, y=275)

    # Create new board using function
    board = engine.new_board()

    # Insert after command then enter mainloop
    root.after(100, lambda : polling(board))
    root.mainloop()
