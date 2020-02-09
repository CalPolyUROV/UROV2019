import cv2
import numpy as np

# Minimim area threshold that is boxed
AREA_THRESHHOLD = 1000

LINE_THICKNESS = 8


# Function that takes in a image and draws boxes around suspicious plants
def box_image(img: np.array) -> np.array:
    """Sample CV method courtesy of the BIG_J
    """
    frame = img
    # Converting image from BGR to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Generating the mask that outlines the plants
    # Method 1: Look for the color green
    mask1 = cv2.inRange(hsv, (30, 30, 30), (70, 255, 255))
    # Method 2

    # Take the mask and clean up the holes in the mask
    # Open removes area of the holes in the mask (removes noise) and
    # then adds area to the holes
    mask1 = cv2.morphologyEx(mask1,
                             cv2.MORPH_OPEN,
                             np.ones((3, 3), np.uint8))
    # Dilate areas in the mask (Add area to the holes in the mask)
    mask1 = cv2.morphologyEx(
        mask1, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8))

    ret, thresh = cv2.threshold(mask1, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    green = (0, 255, 0)
    # rect_list = []  # List of Rectangle objects
    # Loop through each of the "Plant" areas
    for c in contours:
        # if the "Plant" is large enough draw a rectangle around it
        if cv2.contourArea(c) > AREA_THRESHHOLD:
            # get the bounding rect
            x, y, w, h = cv2.boundingRect(c)
            # rect_list.append((x, y, w, h))

            cv2.rectangle(frame,
                          (x, y), (x+w, y+h),
                          green,
                          LINE_THICKNESS)
            # draw a green rectangle to visualize the bounding rect
            # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 15)

    # Demo rectangles
    # for rects in self.rect_list:
    #     x, y, w, h = rects

    return frame
