def convert_to_coord(i):
    # Convert from chess notation to coordinates
    i = i.lower()
    switcher = {
        'a': 0,
        'b': 1,
        'c': 2,
        'd': 3,
        'e': 4,
        'f': 5,
        'g': 6,
        'h': 7
    }
    return switcher.get(i, 99)

def convert_to_alpha(i):
    # Convert to coordinates to chess notation
    switcher = {
        0: 'a',
        1: 'b',
        2: 'c',
        3: 'd',
        4: 'e',
        5: 'f',
        6: 'g',
        7: 'h'
    }
    return switcher.get(i, 'z')

def dist2(p1, p2):
    # Function to calculate dist2, sourced online
    return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

def fuse(points, d):
    # Function to fuse nearby points, sourced online
    ret = []
    d2 = d * d
    n = len(points)
    taken = [False] * n
    for i in range(n):
        if not taken[i]:
            count = 1
            point = [points[i][0], points[i][1]]
            taken[i] = True
            for j in range(i+1, n):
                if dist2(points[i], points[j]) < d2:
                    point[0] += points[j][0]
                    point[1] += points[j][1]
                    count+=1
                    taken[j] = True
            point[0] /= count
            point[1] /= count
            ret.append((int(point[0]), int(point[1])))
    return ret

def place_points(points_row, pieces):
    # Place pixel coordinates of pieces onto the board

    # Sort array
    sorted_row = []
    for x in points_row:
        sort = sorted(x,key=lambda x: x[0])
        sorted_row.append(sort)

    piece_coords = []

    # Calculate location of each chess piece
    for i in pieces:
        x = i[0]
        y = i[1]
        for j in range(0, len(sorted_row)):
            if sorted_row[j][3][1] > y:
                row = j
                break
        for j in range(0, len(sorted_row[row])):
            if sorted_row[row][j][0] > x:
                column = j
                break
        if i[2] > 50:
            piece_coords.append([column, row, i[3][:-5]])

    return piece_coords

def test_board(past_mapped, new_mapped):
    # APPLY 5 UNBREAKABLE MOVE RULES
    # 1 - The number of pieces should not change before and after a move
    # 2 - There can never be more than 16 white pieces
    # 3 - There must always be a king on the board
    # 4 - Total max numbers of particular pieces (e.g. 2 rooks, 2 knights, 9 pawn / queen etc)
    # 5 - There can never be a pawn in the back rank

    # Pawn, rook, knight, bishop, king, queen
    piece_count = [0, 0, 0, 0, 0, 0]
    for x in new_mapped:
        if x[2] == 'white_pawn':
            piece_count[0] = piece_count[0] + 1
        if x[2] == 'white_rook':
            piece_count[1] = piece_count[1] + 1
        if x[2] == 'white_knight':
            piece_count[2] = piece_count[2] + 1
        if x[2] == 'white_bishop':
            piece_count[3] = piece_count[3] + 1
        if x[2] == 'white_king':
            piece_count[4] = piece_count[4] + 1
        if x[2] == 'white_queen':
            piece_count[5] = piece_count[5] + 1

    if (len(new_mapped) != len(past_mapped)):  # Test case 1
        print("FAIL CASE 1")
        return False
    elif len(new_mapped) > 16:  # Test case 2
        print("FAIL CASE 2")
        return False
    elif piece_count[4] != 1: # Test case 3
        print("FAIL CASE 7")
        return False
    # Test case 4
    elif piece_count[0] > 8: # Pawn
        print("FAIL CASE 3")
        return False
    elif piece_count[1] > 2: # Rook
        print("FAIL CASE 4")
        return False
    elif piece_count[2] > 2: # Knight
        print("FAIL CASE 5")
        return False
    elif piece_count[3] > 2: # Bishop
        print("FAIL CASE 6")
        return False
    elif (piece_count[0] + piece_count[5]) > 9: # Pawn + Queen
        print("FAIL CASE 8")
        return False

    return True

def get_move(old_coords, new_coords):
    # Get first moved piece
    for i in new_coords:
        if i not in old_coords:
            print(i)
            end_pos = i

    # Get second move piece
    for i in old_coords:
        if i not in new_coords:
            print(i, "\n")
            start_pos = i

    # Try and convert to a string and return 0000 if failed
    try:
        move = str(convert_to_alpha(start_pos[0]-1)) + str(start_pos[1]) + str(convert_to_alpha(end_pos[0]-1)) + str(end_pos[1])
    except:
        move = "0000" # Set void case

    return move