# Import libraries
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
# Import files
import utility, engine

# Define ID array for use within GUI
id_array = [['W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7'],
            ['W8', 'W9', 'W10', 'W11', 'W12', 'W13', 'W14', 'W15'],
            ['0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0'],
            ['B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15'],
            ['B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']]

# Define the chessboard frame
class chess_board(tk.Frame):
    def __init__(self, parent):
        self.dimension = 8
        self.size = 49
        self.pieces = {}

        tk.Frame.__init__(self, parent)

        self.canvas = tk.Canvas(self, width=(self.dimension * self.size), height=(self.dimension * self.size))
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)
        self.create()

    def create(self):
        self.canvas.delete("square")
        colour = "grey"
        for row in range(self.dimension):
            colour = "white" if colour == "grey" else "grey"
            for col in range(self.dimension):
                x = (col * self.size)
                y = (row * self.size)
                self.canvas.create_rectangle(x, y, (x + self.size), (y + self.size), outline="black", fill=colour)
                colour = "white" if colour == "grey" else "grey"

    def new_piece(self, name, image, row=0, column=0):
        self.canvas.create_image(0, 0, image=image, tags=(name, "piece"), anchor="c") # REMOVE PIECE TAG
        self.set_piece(row, column)

    def move_piece(self, move):
        start_x = utility.convert_to_coord(move[0])
        start_y = int(move[1]) - 1
        end_x = utility.convert_to_coord(move[2])
        end_y = int(move[3]) - 1
        id_array[end_y][end_x] = id_array[start_y][start_x]
        id_array[start_y][start_x] = '0'
        self.set_piece(end_y, end_x)

    def set_piece(self, row, column):
        name = id_array[row][column]
        self.pieces[name] = (row, column)
        x = (column * self.size) + int(self.size/2)
        y = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x, y)

# Define the play frame
class play(tk.Frame):
    def __init__(self, parent):
        # Create labels
        self.parent = parent
        tk.Frame.__init__(self, parent)
        self.frame = ttk.Labelframe(self, text="Play Game", width=390, height=250)
        self.frame.pack()
        self.turn_label = ttk.Label(self.frame, text="Current Turn : NONE", font=("Helvetica", 11))
        self.turn_label.place(x=10, y=10)
        self.evaluation_label = ttk.Label(self.frame, text="Evaluation : NONE", font=("Helvetica", 11))
        self.evaluation_label.place(x=10, y=40)
        self.white_label = ttk.Label(self.frame, text="White Pieces : NONE", font=("Helvetica", 11))
        self.white_label.place(x=10, y=70)
        self.black_label = ttk.Label(self.frame, text="Black Pieces : NONE", font=("Helvetica", 11))
        self.black_label.place(x=10, y=100)

    # Functions to edit labels
    def configure_turn(self, _text):
        self.turn_label.configure(text=_text)

    def configure_evaluation(self, _text):
        self.evaluation_label.configure(text=_text)

    def configure_white(self, _text):
        self.white_label.configure(text=_text)

    def configure_black(self, _text):
        self.black_label.configure(text=_text)

# Define the settings frame
class settings(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, parent)
        self.frame = ttk.Labelframe(self, text="Settings", width=390, height=85)
        self.frame.pack()

        # Create combo box and lock it to read-only
        self.difficulty_entry = ttk.Combobox(self.frame, width=5, textvariable="n", state="readonly")
        self.difficulty_entry['values'] = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
        self.difficulty_entry.current(20)
        self.difficulty_entry.place(x=105, y=5)
        self.difficulty_label = ttk.Label(self.frame, text="Difficulty Level : ")
        self.difficulty_label.place(x=10, y=5)

        # Create hash entry
        self.hash_entry = ttk.Entry(self.frame, width=8)
        self.hash_entry.insert(0, "16")
        self.hash_entry.place(x=105, y=35)
        self.hash_label = ttk.Label(self.frame, text="Hash Size : ")
        self.hash_label.place(x=10, y=35)

        # Apply settings button
        self.apply_settings = ttk.Button(self.frame, text="Apply", command=lambda: engine.configure(self.difficulty_entry.current(), self.hash_entry.get()))
        self.apply_settings.place(x=300, y=35)

# Show warning notification
def show_warning():
    tk.messagebox.showwarning(title="Warning", message="Invalid move detected - please try again!")

# Show error notification
def show_error():
    tk.messagebox.showerror(title="Machine vision error", message="Please make sure camera is not covered")

def is_take(move):
    coord = [(utility.convert_to_coord(move[2])), int(move[3])]
    if id_array[coord[0]][coord[1]] != 0:
        return True
    return False


# Start the GUI
def run():
    # Define root
    root = tk.Tk()

    # Define chess board
    board_frame = chess_board(root)
    board_frame.place(height=400, width=400)

    # Define play frame
    play_frame = play(root)
    play_frame.place(x=400, y=60)

    # Define settings frame
    settings_frame = settings(root)
    settings_frame.place(x=400, y=310)

    # Root setup
    root.geometry("800x400")
    root.resizable(False, False)
    root.title("Chess")
    root.iconbitmap("icon.ico")

    return root, board_frame, play_frame