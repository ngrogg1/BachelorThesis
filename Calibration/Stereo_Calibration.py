# Imports
import cv2
import os
import numpy as np

# Path to the calibration data folder
path = 'C:/Users/nicgr/Documents/GitHub/BachelorThesis/data/Calibration/'

# Matrices for undistortion of frames, which must be computed beforehand with the Mono_Calibration script
# for both cameras
mtx_right = np.load(path + 'Camera_intrinsics/mtx_right.npy')
dist_right = np.load(path + 'Camera_intrinsics/dist_right.npy')
mtx_left = np.load(path + 'Camera_intrinsics/mtx_left.npy')
dist_left = np.load(path + 'Camera_intrinsics/dist_left.npy')

# Images for stereo calibration have to be synchronized!
images_left = os.listdir(path + 'frames_stereo/frames_left')
images_right = os.listdir(path + 'frames_stereo/frames_right')

# Number of checkerboard rows - 1
rows = 6

# Number of checkerboard columns - 1
columns = 8

# The real world square size in one dimension
world_scaling = 0.03

# Coordinates of squares in the checkerboard world space (== Object points)
objp = np.zeros((rows*columns, 3), np.float32)
objp[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
objp = world_scaling * objp

# Get the imagesize of the pictures
imsize = cv2.imread(os.path.join(path, 'frames_stereo/frames_left', images_left[0])).shape[:2][::-1]

# Create arrays which will hold all the object points and their corresponding image points
# of the corners of the chessboard
obj_points = []
imagepoints_left = []
imagepoints_right = []

# Defining the criteria for the calibration
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.0001)

# Iterator to see how many image pairs have been processed
i = 1

# See how many image pairs will be processed
print(f'{len(images_left)} image pairs have to be processed...')

# Loop over every synchronized image pair
for camera_left_frame_name, camera_right_frame_name in zip(images_left, images_right):
    # Read in the images for the left and right camera and preprocess them for the aruco marker detection
    camera_left_frame = cv2.imread(os.path.join(path, 'frames_stereo/frames_left', camera_left_frame_name))
    gray_left_frame = cv2.cvtColor(camera_left_frame, cv2.COLOR_BGR2GRAY)

    camera_right_frame = cv2.imread(os.path.join(path, 'frames_stereo/frames_right', camera_right_frame_name))
    gray_right_frame = cv2.cvtColor(camera_right_frame, cv2.COLOR_BGR2GRAY)

    # Returns if corners have been detected and the positions of internal corners of the chessboard
    res_left = cv2.findChessboardCorners(gray_left_frame, (6, 8), None)
    res_right = cv2.findChessboardCorners(gray_right_frame, (6, 8), None)

    # See if the corners have been detected for both frames
    if res_left[0] is True and res_right[0] is True:
        # Refines the corner locations
        corners_left = cv2.cornerSubPix(gray_left_frame, res_left[1], (11, 11), (-1, -1), criteria)
        corners_right = cv2.cornerSubPix(gray_right_frame, res_right[1], (7, 7), (-1, -1), criteria)

        # Save the image points and the corresponding object points
        obj_points.append(objp)
        imagepoints_left.append(corners_left)
        imagepoints_right.append(corners_right)

        # Visualize the detection in the frames
        cv2.drawChessboardCorners(camera_left_frame, (rows, columns), corners_left, res_left[0])
        img_left = cv2.resize(camera_left_frame, (0, 0), fx=0.25, fy=0.25)
        cv2.imshow(camera_left_frame_name, img_left)

        cv2.drawChessboardCorners(camera_right_frame, (rows, columns), corners_right, res_right[0])
        img_right = cv2.resize(camera_right_frame, (0, 0), fx=0.25, fy=0.25)
        cv2.imshow(camera_right_frame_name, img_right)

    # Wait 1.5 seconds before closing the visualization
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Close all windows
    cv2.destroyAllWindows()

    # Log progress every 5 processed image pairs
    if i % 5 == 0:
        print(i)

    # Every iteration one image pair has been preprocessed
    i += 1

# Calibrate the stereo Setup with fixed camera intrinsics
stereocalibration_flags = cv2.CALIB_FIX_INTRINSIC
ret, CM1, dist1, CM2, dist2, R, T, E, F = cv2.stereoCalibrate(obj_points,
                                                              imagepoints_left,
                                                              imagepoints_right,
                                                              mtx_left, dist_left,
                                                              mtx_right, dist_right,
                                                              imsize,
                                                              criteria=criteria,
                                                              flags=stereocalibration_flags)
print(ret)
# Return the Rotation and Translation matrix, that define the position of the right camera to the left
print('Rotation Matrix: \n', R, "\n")
print('Translation: \n', T, "\n")

# Save the Rotation and Translation matrix
np.save(path + 'Camera_extrinsics/rotation.npy', R)
np.save(path + 'Camera_extrinsics/translation.npy', T)
