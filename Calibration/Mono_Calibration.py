# Imports
import cv2
import numpy as np
import os
import time

# Get ChArUco Board pattern and dictionary to identify aruco markers
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
board = cv2.aruco.CharucoBoard_create(5, 7, 0.03, 0.0175, aruco_dict)

allCorners = []
allIds = []
decimator = 1

images = os.listdir('data/frames_mono')

print(f'{len(images)} images have to be processed...')

for frame_name in images:

    img = cv2.imread(os.path.join('data/frames_mono', frame_name))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = cv2.aruco.detectMarkers(gray,aruco_dict)

    if len(res[0])>0:
        res2 = cv2.aruco.interpolateCornersCharuco(res[0],res[1],gray,board)
        if res2[1] is not None and res2[2] is not None:
            allCorners.append(res2[1])
            allIds.append(res2[2])

            cv2.aruco.drawDetectedMarkers(gray,res[0],res[1])
            cv2.imwrite('data/calibration_output_mono/' + frame_name, gray)

    if decimator % 20 == 0 and decimator > 0 or decimator == len(images):
        print(f'{decimator} of {len(images)} have been processed')

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    decimator+=1

print("Processing finished!")

imsize = cv2.imread(os.path.join('data/frames_mono', images[0])).shape[:2]
start = time.time()
print("Start calibrating camera...")
_, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(allCorners, allIds, board, imsize, None, None)
print(f'Calibration finished in {round((time.time()-start)/60,1)} minutes!')

print("Camera Matrix: \n", cameraMatrix)
print("Camera Distortion Coefficients: \n",distCoeffs)

np.save('data/Camera_intrinsics/mtx.npy', cameraMatrix)
np.save('data/Camera_intrinsics/dist.npy',distCoeffs)

cv2.destroyAllWindows()