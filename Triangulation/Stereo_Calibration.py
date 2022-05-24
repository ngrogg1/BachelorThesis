# Imports
import cv2
import os
import numpy as np

#
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
board = cv2.aruco.CharucoBoard_create(5, 7, 0.03, 0.0175, aruco_dict)

# Matrices for undistortion of frames, which must be computed beforehand with the Mono_Calibration script
mtx = np.load('CalibrationOutput/mtx.npy')
dist = np.load('CalibrationOutput/dist.npy')

# !!! create these folders or get path to camera with opencv. images have to be synchronized
images_left = os.listdir('Frames_left')
images_right = os.listdir('Frames_right')

object_points = []

for y in range(7-1):
    for x in range(5-1):
        x_coordinate = (x + 1) * 0.03
        y_coordinate = (y + 1) * 0.03
        z_coordinate = 0

        corner = [x_coordinate, y_coordinate, z_coordinate]

        object_points.append(corner)

object_points = np.array(object_points, dtype=np.float32)

obj_points = []

allCorners_left = []
allIds_left = []
allCorners_right = []
allIds_right = []

i = 0

print(len(images_left))

for camera_left_frame_name, camera_right_frame_name in zip(images_left, images_right):
    print(i)
    camera_left_frame = cv2.imread(os.path.join('Frames_left', camera_left_frame_name))
    gray_left_frame = cv2.cvtColor(camera_left_frame, cv2.COLOR_BGR2GRAY)
    res_left = cv2.aruco.detectMarkers(gray_left_frame, aruco_dict)

    camera_right_frame = cv2.imread(os.path.join('Frames_left', camera_right_frame_name))
    gray_right_frame = cv2.cvtColor(camera_right_frame, cv2.COLOR_BGR2GRAY)
    res_right = cv2.aruco.detectMarkers(gray_right_frame, aruco_dict)

    if len(res_left[0]) > 0 and len(res_right[0]) > 0:
        res_left2 = cv2.aruco.interpolateCornersCharuco(res_left[0], res_left[1], gray_left_frame, board)
        res_right2 = cv2.aruco.interpolateCornersCharuco(res_right[0], res_right[1], gray_right_frame, board)
        obj_points.append(object_points)
        if res_left2[1] is not None and res_left2[2] is not None:
            allCorners_left.append(res_left2[1])
            allIds_left.append(res_left2[2])

        if res_right2[1] is not None and res_right2[2] is not None:
            allCorners_right.append(res_right2[1])
            allIds_right.append(res_right2[2])

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    i += 1

imsize = cv2.imread(os.path.join('Frames', images_left[0])).shape[:2]

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.0001)
stereocalibration_flags = cv2.CALIB_FIX_INTRINSIC
ret, CM1, dist1, CM2, dist2, R, T, E, F = cv2.stereoCalibrate(obj_points, allCorners_left, allCorners_right, mtx, dist,
mtx, dist, imsize, criteria = criteria, flags=stereocalibration_flags)
a = 1