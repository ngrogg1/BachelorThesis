# Imports
import cv2
import os

# To generate images of the ChArUco board, load the video file first
videopath_left = "E:/Camera_BA/Data/camera_left (G94153639)"
videopath_right = "E:/Camera_BA/Data/camera_right (G88327234)"

# file_left = os.listdir(videopath_left)
# cap = cv2.VideoCapture(videopath_left + file_left[-1])

file_right = os.listdir(videopath_right)
cap = cv2.VideoCapture(videopath_right + file_right[-1])

# Path to the calibration data folder
path = 'C:/Users/nicgr/Documents/GitHub/BachelorThesis/data/Calibration/'

# Iterator to name the frames we want to save
i = 1

# Sets ret to true if the reading of the file was successful (if the video didn't end), and returns a
# numpy array of the image frame in frame
ret, frame = cap.read()

# Iterate over each frame of the video file
while ret:
    # Shows the captured frame of the video file
    cv2.imshow('frame', frame)

    # Takes a snapshot of the image and saves it in the frame directory
    # cv2.imwrite(path + 'frames_mono/frames_left/frame' + str(i) + '.jpg', frame)
    cv2.imwrite(path + 'frames_mono/frames_right/frame' + str(i) + '.jpg', frame)

    i += 1

    # If the key 'q' is pressed, it ends the video capture
    if cv2.waitKey(1) == ord('q'):
        break

    # Sets ret to true if the reading of the file was successful (if the video didn't end), and returns a
    # numpy array of the image frame in frame
    ret, frame = cap.read()

# Release the video file and close all windows
cap.release()
cv2.destroyAllWindows()
