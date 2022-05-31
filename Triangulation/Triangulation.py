# Imports
import cv2
import numpy as np
import torch

def undistort_rectify_frames(mtx_left, dist_left, mtx_right, dist_right, img_size, R, T, frame_left, frame_right):
    # Rectify the images, so that both are horizontally aligned
    R1, R2, P1, P2, _, _, _ = cv2.stereoRectify(mtx_left, dist_left, mtx_right, dist_right, img_size, R, T, 1, (0, 0))
    stereo_map_left = cv2.initUndistortRectifyMap(mtx_left, dist_left, R1, P1, img_size, cv2.CV_16SC2)
    stereo_map_right = cv2.initUndistortRectifyMap(mtx_right, dist_right, R2, P2, img_size, cv2.CV_16SC2)

    stereo_map_left_x = stereo_map_left[0]
    stereo_map_left_y = stereo_map_left[1]

    stereo_map_right_x = stereo_map_right[0]
    stereo_map_right_y = stereo_map_right[1]

    # Undistort and rectify images
    frame_undistorted_l = cv2.remap(frame_left, stereo_map_left_x, stereo_map_left_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
    frame_undistorted_r = cv2.remap(frame_right, stereo_map_right_x, stereo_map_right_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)

    return frame_undistorted_l, frame_undistorted_r, P1, P2


def get_imagepoints(result_left, result_right):
    # Get the center of the bounding boxes for both frames
    df_left = result_left.pandas().xyxy[0].to_numpy()[0]
    x_min_l, y_min_l, x_max_l, y_max_l = df_left[:4]
    df_right = result_right.pandas().xyxy[0].to_numpy()[0]
    x_min_r, y_min_r, x_max_r, y_max_r = df_right[:4]

    center_x_left = int(x_min_l + (x_max_l - x_min_l) / 2)
    center_y_left = int(y_min_l + (y_max_l - y_min_l) / 2)

    center_x_right = int(x_min_r + (x_max_r - x_min_r) / 2)
    center_y_right = int(y_min_r + (y_max_r - y_min_r) / 2)

    return center_x_left, center_y_left, center_x_right, center_y_right


def resize_dispwind(img_shape):
    w, h = img_shape
    h1 = int(w / 2)
    w1 = int(h / 2)

    cv2.namedWindow("frame_left", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("frame_left", w1, h1)

    cv2.namedWindow("frame_right", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("frame_right", w1, h1)


# Path to the data folder
data_path = 'C:/Users/Nic/Documents/GitHub/BachelorThesis/data/'

# Rotation and Translation Matrix which are computed in the Stereo_Calibration script
R = np.load(data_path + 'Calibration/Camera_extrinsics/rotation.npy')
T = np.load(data_path + 'Calibration/Camera_extrinsics/translation.npy')

# Camera intrinsics for both cameras
mtx_left = np.load(data_path + 'Calibration/Camera_intrinsics/mtx_left.npy')
dist_left = np.load(data_path + 'Calibration/Camera_intrinsics/dist_left.npy')
mtx_right = np.load(data_path + 'Calibration/Camera_intrinsics/mtx_right.npy')
dist_right = np.load(data_path + 'Calibration/Camera_intrinsics/dist_right.npy')

# Camera focal length and the baseline
focal_length = 0.016
baseline = 0.16

# Size of the images
img_size = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/test/frame_0_left.jpg').shape[:2]

# RT matrix for C1 is identity.
RT1 = np.concatenate([np.eye(3), [[0], [0], [0]]], axis=-1)
P1 = mtx_left @ RT1  # projection matrix for C1

# RT matrix for C2 is the R and T obtained from stereo calibration.
RT2 = np.concatenate([R, T], axis=-1)
P2 = mtx_right @ RT2  # projection matrix for C2

# Get the camera frames
frame_left = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/test/frame_0_left.jpg', -1)
frame_right = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/test/frame_0_right.jpg', -1)

# frame_left = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/Blender/images/car_000001_left.jpg', -1)
# frame_right = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/Blender/images/car_000001_right.jpg', -1)

frame_undistorted_left, frame_undistorted_right, P_1, P_2 = undistort_rectify_frames(mtx_left, dist_left, mtx_right,
                                                                                   dist_right, img_size, R, T,
                                                                                   frame_left, frame_right)

# Load the yolov5 model which with custom pretrained weights, trained on the blender images
yolo = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/Users/Nic/Documents/GitHub/yolov5/runs/train/exp/weights/last.pt', force_reload=True)

# Make a forward pass to detect objects on the rectified and undistorted frames
# result_left = yolo(frame_left)
# result_right = yolo(frame_right)
result_left = yolo(frame_undistorted_left)
result_right = yolo(frame_undistorted_right)

center_x_l, center_y_l, center_x_r, center_y_r = get_imagepoints(result_left, result_right)

# Calculate the pixel disparity of the center between both frames
disparity = abs(center_x_l - center_x_r)

# Triangulate the center of the bounding box
points3d = cv2.triangulatePoints(P1, P2, (center_x_l, center_y_l), (center_x_r, center_y_r))

# Calculate the distance form the baseline center to the bounding box center
depth = points3d[2]/points3d[3] # focal_length*baseline/(center_x_r - center_x_l) *
x_distance = points3d[0]/points3d[3]
y_distance = points3d[1]/points3d[3]
print(f'Distance form the baseline center to the bounding box center: {round(depth[0],3)} meters')

frame_left = np.squeeze(result_left.render())
frame_left = cv2.circle(frame_left, (center_x_l, center_y_l), 10, (0, 0, 256), -1)

frame_right = np.squeeze(result_right.render())
frame_right = cv2.circle(frame_right, (center_x_r, center_y_r), 10, (0, 0, 256), -1)

resize_dispwind(img_size)
# cv2.imshow('frame_right', frame_undistorted_right)
# cv2.imshow('frame_left', frame_undistorted_left)
# cv2.waitKey(-1)
cv2.imshow("frame_left", frame_left)
cv2.imshow("frame_right", frame_right)

cv2.waitKey(-1)
cv2.destroyAllWindows()
