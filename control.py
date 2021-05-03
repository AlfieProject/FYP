# Import libraries
import math, serial, time
# Import files
import utility


def get_board_coords(move):
    # Convert move from algebraic chess notation to coordinates
    start_coord = [(utility.convert_to_coord(move[0]) + 1), int(move[1])]
    final_coord = [(utility.convert_to_coord(move[2]) + 1), int(move[3])]

    return [start_coord, final_coord]

def get_arm_angles(coords):
    # Calculates angle for arm base
    # Define known parameters
    x = coords[0]
    y = coords[1]

    # Get physical lengths
    x_length = 18.5 + (37 * (x - 1))
    y_length = 18.5 + (37 * (y - 1))

    y_length_from_arm = 125 + (300 - y_length)

    # Get angle (assuming 0 is left lock).

    if x_length < 150:
        x_length = 150 - x_length
        return  90 + round(math.degrees(-1 * math.atan(x_length / y_length_from_arm)) * 1.05)
    elif x_length > 150:
        x_length = x_length - 150
        return 90 + round(math.degrees(math.atan(x_length / y_length_from_arm)) * 1.05)
    elif x_length == 150:
        return 0
    else:
        # Return 999 on an error
        print("Raise error")
        return 999

def get_arm_coords(board_coords):
    # Calculates distances between square and claw base
    # Left side of board
    if board_coords[0] < 5:
        x = 148 - (18.5 + (40 * (board_coords[0] - 1)))
        y = 125 + (18.5 + (40 * (8 - board_coords[1])))
    # Right side of board
    if board_coords[0] > 4:
        x = (18.5 + (40 * (board_coords[0] - 1))) - 148
        y = 125 + (18.5 + (40 * (8 - board_coords[1])))
    # Pythagoras theorem
    x_squared = (x)**2
    y_squared = (y)**2
    distance = math.sqrt(x_squared + y_squared)

    # Return distance in CM
    return (-distance/10)

def get_angles(coords):
    # Define known parameters
    x = coords[0]
    y = coords[1]
    x_squared = (coords[0])**2
    y_squared = (coords[1])**2

    # Define link lengths
    l_zero = 20
    l_one = 20
    l_zero_squared = (l_zero)**2
    l_one_squared = (l_one)**2

    # Calculate angles in radians
    theta_one = math.acos((x_squared + y_squared - l_zero_squared - l_one_squared) / (2 * l_zero * l_one))
    theta_zero = math.atan2(y, x) - math.atan2((l_one * math.sin(theta_one)), (l_zero + (l_one * math.cos(theta_one))))

    # Convert to degrees
    theta_zero = math.degrees(theta_zero)
    theta_one = math.degrees(theta_one)
    theta_three = round(90 - (180 - (theta_one + (theta_zero - 90))))

    # Apply offsets for arm
    theta_zero = round(theta_zero / 1.5)  + 6
    theta_one = round(138 - theta_one)

    return [theta_zero, theta_one, theta_three]

def initialize():
    # Start serial connection
    comm = serial.Serial('COM3', 9600)
    comm.timeout = 1
    time.sleep(3)

    return comm

def reset_arm(comm):
    # Write angles to reset arm
    write_servo_multiple(comm, [40, 0, 60, 180])

def write_servo(comm, ser_num, angle):
    # Write to a single servo
    # Prepare control string
    string = str(ser_num) + ":" + str(angle) + "#"
    print("Writing angle", angle, "to servo", ser_num)

    # Write to serial
    comm.write(string.encode())

def write_servo_multiple(comm, angles):
    # Write to all 4 arm servos excluding claw
    # Crates a single long string separating servos with a hashtag
    serial_string = ""
    # Servo base
    serial_string = serial_string + str(5) + ":" + str(angles[3]) + "#"
    # Servo shoulder
    serial_string = serial_string + str(4) + ":" + str(angles[0]) + "#"
    # Servo Joint
    serial_string = serial_string + str(3) + ":" + str(angles[1]) + "#"
    # Servo Wrist
    serial_string = serial_string + str(2) + ":" + str(angles[2]) + "#"

    # Write to serial
    comm.write(serial_string.encode())

def write_claw(comm, angle):
    # Set claw angle by writing to servo
    if (-1 < angle < 101):
        write_servo(comm, 1, angle)

def standard_move(comm, move):
    # Convert to coordinates
    board_coords = get_board_coords(move)

    # Open claws
    write_claw(comm, 60)
    time.sleep(1)

    # STARTING LOCATION
    arm_coords = get_arm_coords(board_coords[0])
    # Move above
    angles = get_angles([arm_coords, 10])
    angles.append(get_arm_angles(board_coords[0]))
    write_servo_multiple(comm, angles)
    time.sleep(5)

    # Move around
    angles = get_angles([arm_coords, 5.5])
    angles.append(get_arm_angles(board_coords[0]))
    write_servo_multiple(comm, angles)
    time.sleep(3)

    write_claw(comm, 100)
    time.sleep(3)

    # Move above
    angles = get_angles([arm_coords, 12])
    angles.append(get_arm_angles(board_coords[0]))
    write_servo_multiple(comm, angles)
    time.sleep(3)

    # ENDING LOCATION
    arm_coords = get_arm_coords(board_coords[1])
    # Move above
    angles = get_angles([arm_coords, 10])
    angles.append(get_arm_angles(board_coords[1]))
    write_servo_multiple(comm, angles)
    time.sleep(3)

    # Move around
    angles = get_angles([arm_coords, 5.5])
    angles.append(get_arm_angles(board_coords[1]))
    write_servo_multiple(comm, angles)
    time.sleep(3)

    # Open claws
    write_claw(comm, 0)
    time.sleep(3)

    # Move above
    angles = get_angles([arm_coords, 10])
    angles.append(get_arm_angles(board_coords[1]))
    write_servo_multiple(comm, angles)
    time.sleep(3)

    reset_arm(comm)
    time.sleep(2)

def take_move(comm, move):
    # Convert board coordinates
    board_coords = get_board_coords(move)

    # Open claws
    write_claw(comm, 60)
    time.sleep(1)

    # STARTING LOCATION
    # Move above piece to take
    arm_coords = get_arm_coords(board_coords[1])
    angles = get_angles([arm_coords, 10])
    angles.append(get_arm_angles(board_coords[1]))
    write_servo_multiple(comm, angles)
    time.sleep(3)

    # Move around piece to take
    angles = get_angles([arm_coords, 5.5])
    angles.append(get_arm_angles(board_coords[1]))
    write_servo_multiple(comm, angles)
    time.sleep(3)

    # Close claws
    write_claw(comm, 100)
    time.sleep(3)

    # Move above piece to take
    angles = get_angles([arm_coords, 12])
    angles.append(get_arm_angles(board_coords[1]))
    write_servo_multiple(comm, angles)
    time.sleep(3)

    # Move next to board
    write_servo_multiple(comm, [70, 75, 70, 20])
    [70, 75, 70, 20]
    time.sleep(3)

    # Open claws
    write_claw(comm, 100)
    time.sleep(3)

    # Move up
    write_servo_multiple(comm, [60, 65, 70, 20])
    time.sleep(3)

    # Perform move as standard
    standard_move(comm, move)

