# Import libraries
import cv2
import tensorflow as tf
from utils import visualization_utils as vis_util
import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import LineString
# Import files
import utility

def run_detection(detection_graph, category_index, image_np):

    # Perform detection on an image and return pixel coordinates of each piece
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

            # Each box represents a part of the image where a particular object was detected.
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            # Actual detection.
            (boxes, scores, classes, num_detections) = sess.run([boxes, scores, classes, num_detections], feed_dict={image_tensor: image_np_expanded})

            coordinates = vis_util.return_coordinates(
                image_np,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8,
                min_score_thresh=0.80)

            # Draw circle at coordinates on debug image
            for i in coordinates:
                cv2.circle(image_np, (i[0], i[1]), 25, (0 , 0, 255))

            return coordinates

def get_difference(starting_im, ending_im):
    # Currently not used, backup solution if needed
    # Process starting image
    starting_difference = cv2.subtract(starting_im, ending_im)
    starting_conv_hsv_gray = cv2.cvtColor(starting_difference, cv2.COLOR_BGR2GRAY)
    starting_ret, starting_mask = cv2.threshold(starting_conv_hsv_gray, 0, 255,cv2.THRESH_BINARY_INV |cv2.THRESH_OTSU)

    # Process ending image
    ending_difference = cv2.subtract(ending_im, starting_im)
    ending_conv_hsv_gray = cv2.cvtColor(ending_difference, cv2.COLOR_BGR2GRAY)
    ending_ret, ending_mask = cv2.threshold(ending_conv_hsv_gray, 0, 255,cv2.THRESH_BINARY_INV |cv2.THRESH_OTSU)

    # Apply starting masks
    starting_difference[starting_mask != 255] = [0, 0, 255]
    starting_im[starting_mask != 255] = [0, 0, 255]

    # Apply ending masks
    ending_difference[ending_mask != 255] = [0, 0, 255]
    starting_im[ending_mask != 255] = [0, 255, 0]

    # Find movements made using contours
    contours_end, hierarchy = cv2.findContours(ending_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_start, hierarchy = cv2.findContours(starting_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    points = []

    for c in contours_end:
        # Get information about each contour
        M = cv2.moments(c)
        A = cv2.contourArea(c)

        # If area greater than 100,000 get coordinates and add to array of points
        if A > 100000:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(starting_im, (int(cX), int(cY)), 25, (0, 0, 255))
            points.append((cX, cY))

    for c in contours_start:
        # Get information about each contour
        M = cv2.moments(c)
        A = cv2.contourArea(c)

        # If area less than 100,000 get coordinates and add to array of points
        if A > 100000:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(starting_im, (int(cX), int(cY)), 25, (0, 255, 0))
            points.append((cX, cY))

    # Write debug images to file
    cv2.imwrite('diff.png', starting_im)
    plt.subplot(121), plt.imshow(starting_im, cmap='gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(ending_im, cmap='gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
    plt.show()

def get_board(image):
    # Function to get coordinates of board using openCV
    # Perform canny edge detection
    edges = cv2.Canny(image, 100, 200)

    # Dilate the image
    kernel = np.ones((5, 5), np.uint8)
    new_edge = cv2.dilate(edges,kernel,iterations = 1)
    opening = cv2.morphologyEx(new_edge, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

    # Get hough lines
    lines = cv2.HoughLinesP(closing, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=20)

    verticalLines = []
    horizontalLines = []

    # Calculate angle of each line based of coordinates
    # Add each line to the appropriate array
    for line in lines:
        x1, y1, x2, y2 = line[0]
        m = (y2 - y1) / (x2 - x1)
        m = abs(m)
        if m > 3:
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
            horizontalLines.append(line[0])
        else:
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            verticalLines.append(line[0])

    # LINE ONE IS VERTICAL
    # LINE TWO IS HORIZONTAL

    points = []

    # Calculate line intersections using shapley libraries
    for i in range(0, len(verticalLines)):
        one_x1, one_y1, one_x2, one_y2 = verticalLines[i]
        for j in range(0, len(horizontalLines)):
            two_x1, two_y1, two_x2, two_y2 = horizontalLines[j]

            line1 = LineString([(one_x1, one_y1), (one_x2, one_y2)])
            line2 = LineString([(two_x1, two_y1), (two_x2, two_y2)])

            int_pt = line1.intersection(line2)
            try:
                x = int(int_pt.x)
                y = int(int_pt.y)
                points.append([x, y])
            except:
                None

    # joint nearby points together of within a circle of diameter 10 pixels
    inter = utility.fuse(points, 10)

    # Draw circles on image
    for x in inter:
        cv2.circle(image, (int(x[0]), int(x[1])), radius=5, color=(0, 0, 255), thickness=-1)

    # Sort intersection points
    sorted_points = sorted(inter,key=lambda x: x[1])

    point_row = []
    temp = []

    # Split points into rows and add to a 2D array
    for x in range (0, len(sorted_points)):
        temp.append(sorted_points[x])
        if ((x + 1) % 9) == 0:
            point_row.append(temp)
            temp = []

    # Write images for debug
    cv2.imwrite('board_detection.jpeg', image)
    cv2.imwrite('im_test.png', image)
    cv2.imwrite('ed_test.png', edges)

    return point_row
