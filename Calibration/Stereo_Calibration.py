# Imports
import cv2
import os
import numpy as np

# Matrices for undistortion of frames, which must be computed beforehand with the Mono_Calibration script
mtx = np.load('data/Camera_intrinsics/mtx.npy')
dist = np.load('data/Camera_intrinsics/dist.npy')

# Images have to be synchronized!
images_left = os.listdir('data/frames_stereo/frames_left')
images_right = os.listdir('data/frames_stereo/frames_right')

rows = 6  # number of checkerboard rows - 1.
columns = 8  # number of checkerboard columns - 1.
world_scaling = 0.03  # change this to the real world square size

# coordinates of squares in the checkerboard world space
objp = np.zeros((rows * columns, 3), np.float32)
objp[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
objp = world_scaling * objp

obj_points = []

imagepoints_left = []
imagepoints_right = []

imsize = cv2.imread(os.path.join('data/frames_stereo/frames_left', images_left[0])).shape[:2]

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.0001)

i = 0

print(len(images_left))

for camera_left_frame_name, camera_right_frame_name in zip(images_left, images_right):
    print(i)
    camera_left_frame = cv2.imread(os.path.join('data/frames_stereo/frames_left', camera_left_frame_name))
    gray_left_frame = cv2.cvtColor(camera_left_frame, cv2.COLOR_BGR2GRAY)
    res_left = cv2.findChessboardCorners(gray_left_frame, (rows, columns), None)

    camera_right_frame = cv2.imread(os.path.join('data/frames_stereo/frames_right', camera_right_frame_name))
    gray_right_frame = cv2.cvtColor(camera_right_frame, cv2.COLOR_BGR2GRAY)
    res_right = cv2.findChessboardCorners(gray_right_frame, (rows, columns), None)

    if res_left[0] is True and res_right[0] is True:

        corners_left = cv2.cornerSubPix(gray_left_frame, res_left[1], (11, 11), (-1, -1), criteria)
        corners_right = cv2.cornerSubPix(gray_right_frame, res_right[1], (11, 11), (-1, -1), criteria)

        obj_points.append(objp)
        imagepoints_left.append(corners_left)
        imagepoints_right.append(corners_right)

        cv2.drawChessboardCorners(camera_left_frame, (rows, columns), corners_left, res_left[0])
        img_left = cv2.resize(camera_left_frame, (0,0), fx=0.25, fy=0.25)
        cv2.imshow('camera_left_frame', img_left)

        cv2.drawChessboardCorners(camera_right_frame, (rows, columns), corners_right, res_right[0])
        img_right = cv2.resize(camera_right_frame, (0,0), fx=0.25, fy=0.25)
        cv2.imshow('camera_right_frame', img_right)


    if cv2.waitKey(1500) & 0xFF == ord('q'):
        break
    cv2.destroyAllWindows()
    i += 1

stereocalibration_flags = cv2.CALIB_FIX_INTRINSIC
ret, CM1, dist1, CM2, dist2, R, T, E, F = cv2.stereoCalibrate(obj_points,
                                                              imagepoints_left,
                                                              imagepoints_right,
                                                              mtx, dist,
                                                              mtx, dist,
                                                              imsize,
                                                              criteria=criteria,
                                                              flags=stereocalibration_flags)
print('Rotation Matrix: \n', R)
print('Translation: \n', T)

np.save('data/Camera_extrinsics/rotation.npy', R)
np.save('data/Camera_extrinsics/translation.npy', T)