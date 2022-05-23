import cv2
from cv2 import aruco
import numpy as np

cap = cv2.VideoCapture(0)

mtx = np.load('CalibrationOutput/mtx.npy')
dist = np.load('CalibrationOutput/dist.npy')

ret = True

while  ret:
    ret, frame = cap.read()

    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # undistort
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

    # crop the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]


    dst = cv2.resize(dst, (0,0), fx=4, fy=4)
    cv2.imshow('frame_undistortet',dst)
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()