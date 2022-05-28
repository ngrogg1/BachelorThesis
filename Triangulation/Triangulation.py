import cv2
import numpy as np
import torch
from matplotlib import pyplot as plt

# Rotation and Translation Matrix which are computed in the Stereo_Calibration script
R = np.load('C:/Users/Nic/Documents/GitHub/BachelorThesis/Calibration/data/Camera_extrinsics/rotation.npy')
T = np.load('C:/Users/Nic/Documents/GitHub/BachelorThesis/Calibration/data/Camera_extrinsics/translation.npy')

mtx = np.load('C:/Users/Nic/Documents/GitHub/BachelorThesis/Calibration/data/Camera_intrinsics/mtx.npy')
dist = np.load('C:/Users/Nic/Documents/GitHub/BachelorThesis/Calibration/data/Camera_intrinsics/dist.npy')

img_size = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/images/car_' + f'{str(1).zfill(6)}' + '_left.jpg').shape[:2]

R1, R2, P1, P2, _, _, _ =cv2.stereoRectify(mtx, dist, mtx, dist, img_size, R, T, 1, (0, 0))
stereo_map_left = cv2.initUndistortRectifyMap(mtx, dist, R1, P1, img_size, cv2.CV_16SC2)
stereo_map_right = cv2.initUndistortRectifyMap(mtx, dist, R2, P2, img_size, cv2.CV_16SC2)

stereo_map_left_x = stereo_map_left[0]
stereo_map_left_y = stereo_map_left[1]

stereo_map_right_x = stereo_map_right[0]
stereo_map_right_y = stereo_map_right[1]


# Overlapping world coordinates with the coordinates of the left camera
# RT matrix for left camera is identity.
RT_left = np.concatenate([np.eye(3), [[0],[0],[0]]], axis = -1)
Projection_mtx_left = mtx @ RT_left #projection matrix for C1

# RT matrix for right camera is the R and T obtained from stereo calibration.
RT_right = np.concatenate([R, T], axis = -1)
Projection_mtx_right = mtx @ RT_right #projection matrix for C2

focal_length = 0.016
baseline = 0.15

yolo = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/Users/Nic/Documents/GitHub/yolov5/runs/train/exp/weights/last.pt', force_reload=True)

frame_left = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/images/car_' + f'{str(1).zfill(6)}' + '_left.jpg', -1)
frame_right = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/images/car_' + f'{str(1).zfill(6)}' + '_right.jpg', -1)

frame_left = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/test/frame_0_left.jpg', -1)
frame_right = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/test/frame_0_right.jpg', -1)

# Undistort and rectify images
frame_undisorted_left = cv2.remap(frame_left, stereo_map_left_x, stereo_map_left_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
frame_undisorted_right = cv2.remap(frame_right, stereo_map_right_x, stereo_map_right_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
cv2.imshow('frame', frame_undisorted_right)
cv2.waitKey(-1)
result_left = yolo(frame_undisorted_left)
result_right = yolo(frame_undisorted_right)

df_left = result_left.pandas().xyxy[0].to_numpy()[0]
x_min_l, y_min_l, x_max_l, y_max_l = df_left[:4]
df_right = result_right.pandas().xyxy[0].to_numpy()[0]
x_min_r, y_min_r, x_max_r, y_max_r = df_right[:4]

center_x_l = int(x_min_l + (x_max_l - x_min_l)/2)
center_y_l = int(y_min_l + (y_max_l - y_min_l)/2)

center_x_r = int(x_min_r + (x_max_r - x_min_r)/2)
center_y_r = int(y_min_r + (y_max_r - y_min_r)/2)

disparity = abs(center_x_l - center_x_r)

points3d = cv2.triangulatePoints(P1,
                                 P2,
                                 (center_x_l, center_y_l),
                                 (center_x_r, center_y_r))

depth = focal_length*baseline/(center_x_r - center_x_l) * points3d[2]/points3d[3]

print(depth)

frame_left = np.squeeze(result_left.render())
frame_left = cv2.circle(frame_left, (center_x_l, center_y_l), 10, (0, 0, 256), -1)

frame_right = np.squeeze(result_right.render())
frame_right = cv2.circle(frame_right, (center_x_r, center_y_r), 10, (0, 0, 256), -1)

w, h = img_size
w1 = int(w/2)
h1 = int(h/2)

cv2.namedWindow("image_left",cv2.WINDOW_NORMAL)
cv2.resizeWindow("image_left", h1, w1)

cv2.namedWindow("image_right",cv2.WINDOW_NORMAL)
cv2.resizeWindow("image_right", h1, w1)

cv2.imshow("image_left", frame_left)
cv2.imshow("image_right", frame_right)

cv2.waitKey(-1)
cv2.destroyAllWindows()
