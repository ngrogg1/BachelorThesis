import cv2
from cv2 import aruco
import numpy as np
from scipy.spatial.transform import Rotation


def rvec2eul(rvec, ids):
    """
    Converts rotational vectors to eular angles, of all detected aruco marker ids.
    :param rvec: rotational vectors
    :param ids: aruco marker ids
    :return: euler angles of all aruco marker ids
    """

    # Convert rotational vector to rotational matrix
    rot_mat = Rotation.from_rotvec([rvec[0][0]])

    # Convert rotational matrix to euler angle vector
    rvec_eul1 = rot_mat.as_euler('xyz', degrees=True)

    # Loop through all the aruco marker's rotation vectors
    for i in range(1, ids):
        # Convert rotational vector of current aruco marker to rotational matrix
        rot_mat = Rotation.from_rotvec([rvec[i][0]])

        # Convert rotational matrix to euler angle vector
        r_eul = rot_mat.as_euler('xyz', degrees=True)

        # Append euler vector of current aruco marker to euler vectors of all detected aruco markers
        rvec_eul1 = np.concatenate((rvec_eul1, r_eul), axis=0)

    return rvec_eul1


def arucocenter(corners, ids):
    """
    Computes the x and y coordinates of the centers of the detected aruco markers based on the
    corners of the aruco markers.
    :param corners: All 4 corners of every detected aruco marker
    :param ids: Ids of all the aruco markers
    :return: The x and y coordinates (in pixels) of the centers of the detected aruco markers
    """

    # To compute the center pixels of an aruco marker, we first add all the corresponding coordinates
    # of the corners of the aruco marker and then take the average as the center pixel
    x_sum = corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]
    y_sum = corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]

    x_centerPixel = np.array(int(x_sum * .25))
    y_centerPixel = np.array(int(y_sum * .25))

    # Repeat this step for all the detected aruco markers
    for i in range(1, ids):
        x_sum = corners[i][0][0][0] + corners[i][0][1][0] + corners[i][0][2][0] + corners[i][0][3][0]
        y_sum = corners[i][0][0][1] + corners[i][0][1][1] + corners[i][0][2][1] + corners[i][0][3][1]

        x_centerPixel = np.stack((x_centerPixel, np.array(int(x_sum * .25))), axis=0)
        y_centerPixel = np.stack((y_centerPixel, np.array(int(y_sum * .25))), axis=0)

    return (x_centerPixel, y_centerPixel)


def minxmaxycorner(corners, ids):
    """
    Computes the bottom left corner of the unrotated bounding box of an aruco marker. This corresponds
    to the minimum x and maximum y coordinate of the corners of an aruco marker.
    :param corners: All the corners of the detected aruco markers
    :param ids: All the ids of the detected aruco markers
    :return: The location of the bottom left corner coordinates of the unrotated bounding box,
             in the corner vectors of the aruco markers
    """

    # Compute which x coordinate of all 4 corners of an aruco marker is the smallest and get the
    # location of this coordinate in the corner vector
    x_array = np.argmin(np.array([corners[0][0][0][0], corners[0][0][1][0], corners[0][0][2][0], corners[0][0][3][0]]))
    x_all = x_array

    # Compute which y coordinate of all 4 corners of an aruco marker is the smallest and get the
    # location of this coordinate in the corner vector
    y_array = np.argmax(np.array([corners[0][0][0][1], corners[0][0][1][1], corners[0][0][2][1], corners[0][0][3][1]]))
    y_all = y_array

    # repeat this step for all the detected aruco markers
    for i in range(1, ids):
        x_array = np.argmin(
            np.array([corners[i][0][0][0], corners[i][0][1][0], corners[i][0][2][0], corners[i][0][3][0]]))
        y_array = np.argmax(
            np.array([corners[i][0][0][1], corners[i][0][1][1], corners[i][0][2][1], corners[i][0][3][1]]))
        if ids < 2:
            x_all = np.concatenate((np.array(x_all), x_array), axis=0)
            y_all = np.concatenate((np.array(y_all), y_array), axis=0)
        else:
            x_all = np.stack((np.array(x_all), x_array), axis=0)
            y_all = np.stack((np.array(y_all), y_array), axis=0)

    return x_all, y_all


# Load aruco dictionaries
arucoDict = aruco.Dictionary_get(aruco.DICT_5X5_1000)
arucoParams = aruco.DetectorParameters_create()

# Matrices for undistortion of frames, which must be computed beforehand with the CameraCalibration script
mtx = np.load('CalibrationOutput/mtx.npy')
dist = np.load('CalibrationOutput/dist.npy')

# Start capturing webcam
cap = cv2.VideoCapture(0)

# Set return value to true to start the first iteration of the webcam capture
ret = True

# Loop over webcam frames as long as it is recording
while ret:

    # Sets ret to true if the reading of the file was successful (if the video didn't end), and returns a
    # numpy array of the image frame in frame
    ret, frame = cap.read()

    # Get height and width of the frame
    h, w = frame.shape[:2]

    #
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # Undistort the frame
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

    # Crop the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    # Detect the aruco markers
    gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)
    frame_markers = aruco.drawDetectedMarkers(dst.copy(), corners, ids)

    # Rotational and translational vectors of ArucoMarkerPosition
    rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)

    # Restart while loop if no markers detected
    if ids is None:
        frame_markers = cv2.resize(frame_markers, (0, 0), fx=4, fy=4)
        cv2.imshow('frame', frame_markers)

        if cv2.waitKey(1) == ord('q'):
            break

        continue

    # Convert rotational vector to euler angles of detected aruco markers
    rvec_eul = rvec2eul(rvec, len(ids))

    # Get the location of the bottom left corner of the unrotated bounding box of an aruco marker
    x_min, y_max = minxmaxycorner(corners, len(ids))

    # Show how the camera has to be turned to get an orthogonal projection on the respective aruco marker
    for i in range(len(ids)):
        cv2.drawFrameAxes(frame_markers, mtx, dist, rvec[i][0], tvec[i][0], 0.05)
        if len(ids) >= 2:
            cv2.putText(frame_markers, 'X-angle:' + str(int(180 - rvec_eul[i][0])),
                        (int(corners[i][0][x_min[i]][0]), int(corners[i][0][y_max[i]][1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(frame_markers, 'Y-angle:' + str(int(180 - rvec_eul[i][1])),
                        (int(corners[i][0][x_min[i]][0]), int(corners[i][0][y_max[i]][1]) + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(frame_markers, 'Z-angle:' + str(int(180 - rvec_eul[i][2])),
                        (int(corners[i][0][x_min[i]][0]), int(corners[i][0][y_max[i]][1]) + 20),
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
