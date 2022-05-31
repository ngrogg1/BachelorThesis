# Imports
import cv2
import numpy as np
import os
import time

# Get ChArUco Board pattern and dictionary to identify aruco markers
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
board = cv2.aruco.CharucoBoard_create(5, 7, 0.03, 0.0175, aruco_dict)

# Create arrays which will hold all the image points of the corners of the aruco markers and their
# corresponding ids
allCorners_left = []
allIds_left = []
allCorners_right = []
allIds_right = []

# Iterator to see how many pictures have been processed
decimator = 1

# Path to the calibration data folder
path = 'C:/Users/Nic/Documents/GitHub/BachelorThesis/data/Calibration/'

# All images which are used for the calibration of a single camera
images_left = os.listdir(path + 'frames_mono/frames_left')
images_right = os.listdir(path + 'frames_mono/frames_right')

# See how many pictures will be processed
print(f'{len(images_left)} images for the left camera and {len(images_right)} images for the right camera '
      f'have to be processed...')

# Loop over every single image
for frame_name_left, frame_name_right in zip(images_left, images_right):
    # Read in the images which are in the frames_mono folder and preprocess them for the aruco marker detection
    img_left = cv2.imread(os.path.join(path, 'frames_mono/frames_left/', frame_name_left))
    gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)

    img_right = cv2.imread(os.path.join(path, 'frames_mono/frames_right/', frame_name_right))
    gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

    # Returns for each detected marker the four corner coordinates as image points and their ids
    # also returns the rejected image points
    res_left = cv2.aruco.detectMarkers(gray_left, aruco_dict)
    res_right = cv2.aruco.detectMarkers(gray_right, aruco_dict)

    # If there are more than 4 markers the function calibrateCameraCharuco can be executed, so we have
    # to make sure there are more 4 markers (more than 16 corners)
    if len(res_left[0]) >= 16:
        # Interpolates the position of the ChArUco board corners and returns their id
        res_left2 = cv2.aruco.interpolateCornersCharuco(res_left[0], res_left[1], gray_left, board)

        # If the chessboard corners could be identified we store these imagepoints and their ids
        if res_left2[1] is not None and res_left2[2] is not None:
            allCorners_left.append(res_left2[1])
            allIds_left.append(res_left2[2])

            # Saving the images with the detected markers for inspection
            cv2.aruco.drawDetectedMarkers(gray_left, res_left[0], res_left[1])
            cv2.imwrite(path + 'calibration_output_mono/left_camera/' + frame_name_left, gray_left)

    # If there are more than 4 markers the function calibrateCameraCharuco can be executed, so we have
    # to make sure there are more 4 markers (more than 16 corners)
    if len(res_right[0]) >= 16:
        # Interpolates the position of the ChArUco board corners and returns their id
        res_right2 = cv2.aruco.interpolateCornersCharuco(res_right[0], res_right[1], gray_right, board)

        # If the chessboard corners could be identified we store these imagepoints and their ids
        if res_right2[1] is not None and res_right2[2] is not None:
            allCorners_right.append(res_right2[1])
            allIds_right.append(res_right2[2])

            # Saving the images with the detected markers for inspection
            cv2.aruco.drawDetectedMarkers(gray_right, res_right[0], res_right[1])
            cv2.imwrite(path + 'calibration_output_mono/right_camera/' + frame_name_right, gray_right)

    # Log progress every 20 processed images
    if decimator % 20 == 0 and 0 < decimator < len(images_left) or decimator == len(images_left):
        print(f'{decimator} of {len(images_left)} images of the left camera have been processed')
    if decimator % 20 == 0 and 0 < decimator < len(images_right) or decimator == len(images_right):
        print(f'{decimator} of {len(images_right)} images of the right camera have been processed')

    # Abort loop by pressing q on keyboard
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Every iteration one image has been preprocessed
    decimator += 1

print("Processing finished for both cameras! \n")

# Get the imagesize of the pictures
imsize = cv2.imread(os.path.join(path, 'frames_mono/frames_left/', images_left[0])).shape[:2]

print("Start calibrating left camera...")

# To see how long the calibration of the camera takes
start = time.time()

# Calibration of the Camera
_, cameraMatrix_left, distCoeffs_left, _, _ = cv2.aruco.calibrateCameraCharuco(allCorners_left,
                                                                               allIds_left, board,
                                                                               imsize, None, None)
print(f'Calibration for left camera finished in {round((time.time() - start) / 60, 1)} minutes!')

print("Start calibrating right camera...")

# To see how long the calibration of the camera takes
start = time.time()

# Calibration of the Camera
_, cameraMatrix_right, distCoeffs_right, _, _ = cv2.aruco.calibrateCameraCharuco(allCorners_right,
                                                                                 allIds_right,
                                                                                 board,
                                                                                 imsize, None, None)
print(f'Calibration for right camera finished in {round((time.time() - start) / 60, 1)} minutes!')

# Show the results of the Calibration
print("Left Camera Matrix: \n", cameraMatrix_left, "\n")
print("Left Camera Distortion Coefficients: \n", distCoeffs_left, "\n")
print("Right Camera Matrix: \n", cameraMatrix_right, "\n")
print("Right Camera Distortion Coefficients: \n", distCoeffs_right, "\n")

# Save the camera matrix and distortion coefficient for the stereo calibration and triangulation
np.save(path + 'Camera_intrinsics/mtx_left.npy', cameraMatrix_left)
np.save(path + 'Camera_intrinsics/dist_left.npy', distCoeffs_left)
np.save(path + 'Camera_intrinsics/mtx_right.npy', cameraMatrix_right)
np.save(path + 'Camera_intrinsics/dist_right.npy', distCoeffs_right)

# Close all windows if any have been opened
cv2.destroyAllWindows()
