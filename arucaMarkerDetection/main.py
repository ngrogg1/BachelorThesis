import cv2
from cv2 import aruco
import numpy as np
from scipy.spatial.transform import Rotation

# convert rotational vectors to euler angles (of all detected aruco marker ids)
def rvec2eul(rvec, ids):
    rvec_eul1 = Rotation.from_rotvec([rvec[0][0]])
    rvec_eul1 = rvec_eul1.as_euler('xyz', degrees=True)

    for i in range(1, ids):
        r = Rotation.from_rotvec([rvec[i][0]])
        r = r.as_euler('xyz', degrees=True)
        rvec_eul1 = np.concatenate((rvec_eul1, r), axis=0)

    return rvec_eul1

def arucocenter(corners, ids):
    x_sum = corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]
    y_sum = corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]

    x_centerPixel = np.array(int(x_sum * .25))
    y_centerPixel = np.array(int(y_sum * .25))

    for i in range(1,ids):
        x_sum = corners[i][0][0][0] + corners[i][0][1][0] + corners[i][0][2][0] + corners[i][0][3][0]
        y_sum = corners[i][0][0][1] + corners[i][0][1][1] + corners[i][0][2][1] + corners[i][0][3][1]

        x_centerPixel = np.stack((x_centerPixel, np.array(int(x_sum * .25))), axis = 0)
        y_centerPixel = np.stack((y_centerPixel, np.array(int(y_sum * .25))), axis = 0)

    return (x_centerPixel, y_centerPixel)

def minxmaxycorner(corners, ids):
    x_array = np.argmin(np.array([corners[0][0][0][0], corners[0][0][1][0], corners[0][0][2][0], corners[0][0][3][0]]))
    x_all = x_array
    y_array = np.argmax(np.array([corners[0][0][0][1], corners[0][0][1][1], corners[0][0][2][1], corners[0][0][3][1]]))
    y_all = y_array

    for i in range(1, ids):
        x_array = np.argmin(np.array([corners[i][0][0][0], corners[i][0][1][0], corners[i][0][2][0], corners[i][0][3][0]]))
        y_array = np.argmax(np.array([corners[i][0][0][1], corners[i][0][1][1], corners[i][0][2][1], corners[i][0][3][1]]))
        if ids <2:
            x_all = np.concatenate((np.array(x_all), x_array), axis=0)
            y_all = np.concatenate((np.array(y_all), y_array), axis=0)
        else:
            x_all = np.stack((np.array(x_all), x_array), axis = 0)
            y_all = np.stack((np.array(y_all), y_array), axis = 0)

    return (x_all, y_all)

# load aruco dictionaries
arucoDict = aruco.Dictionary_get(aruco.DICT_5X5_1000)
arucoParams = aruco.DetectorParameters_create()

# matrices for undistortion of frames
mtx = np.load('CalibrationOutput/mtx.npy')
dist = np.load('CalibrationOutput/dist.npy')

cap = cv2.VideoCapture(0)

ret = True

while ret:
    ret, frame = cap.read()

    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # undistort
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

    # crop the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    # detect the aruco markers
    gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)
    frame_markers = aruco.drawDetectedMarkers(dst.copy(), corners, ids)

    # Rotational and Translational Matrices of ArucoMarkerPosition
    rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)

    # restart while loop if no markers detected
    if ids is None:
        frame_markers = cv2.resize(frame_markers, (0, 0), fx=4, fy=4)
        cv2.imshow('frame', frame_markers)

        if cv2.waitKey(1) == ord('q'):
            break

        continue

    # Convert rotational Vector to Euler angles of detected Aruco Markers
    rvec_eul = rvec2eul(rvec, len(ids))

    # print axes of aruco markers
    x_min, y_max = minxmaxycorner(corners, len(ids))

    for i in range(len(ids)):
        cv2.drawFrameAxes(frame_markers, mtx, dist, rvec[i][0], tvec[i][0], 0.05)
        if len(ids)>=2:
            cv2.putText(frame_markers, 'X-angle:' + str(int(180 - rvec_eul[i][0])),
                        (int(corners[i][0][x_min[i]][0]), int(corners[i][0][y_max[i]][1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(frame_markers, 'Y-angle:' + str(int(180 - rvec_eul[i][1])),
                        (int(corners[i][0][x_min[i]][0]), int(corners[i][0][y_max[i]][1])+10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(frame_markers, 'Z-angle:' + str(int(180 - rvec_eul[i][2])),
                        (int(corners[i][0][x_min[i]][0]), int(corners[i][0][y_max[i]][1])+20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 0), 1, cv2.LINE_AA)
        else:
            cv2.putText(frame_markers, 'X-axis-angle:' + str(int(180 - rvec_eul[i][0])),
                        (int(corners[i][0][x_min][0]), int(corners[i][0][y_max][1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 0), 1, cv2.LINE_AA)


    x_centers, y_centers = arucocenter(corners, len(ids))

    frame_markers = cv2.resize(frame_markers, (0, 0), fx=4, fy=4)
    cv2.imshow('frame', frame_markers)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
