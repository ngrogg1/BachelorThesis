# -- coding: utf-8 --
import sys
import threading
from tkinter import *
from tkinter.messagebox import *
import _tkinter
import tkinter.messagebox
import tkinter as tk
import sys, os
from tkinter import ttk
import time
import queue
import numpy as np
import torch
import cv2
import matplotlib
matplotlib.use('TkAgg')
import math

#C:/Users/Nic/Documents/GitHub/BachelorThesis/Triangulation/MvImport

sys.path.append("../MvImport")
from MvCameraControl_class import *
from CamOperation_class import *
from PIL import Image,ImageTk


def To_hex_str(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr


# ch:枚举相机 | en:enum devices
def enum_devices(deviceList, devList, tlayerType):
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)

    if ret != 0:
        print('Error: enum devices fail! ret = ' + ToHexStr(ret))

    if deviceList.nDeviceNum == 0:
        print('Info: Found no device!')

    print("Found %d devices!\n" % deviceList.nDeviceNum)

    devList = []
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents

        # Print USB device information
        if mvcc_dev_info.nTLayerType == MV_USB_DEVICE:  # we use usb
            print("u3v device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print("Device model name: %s" % strModeName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print("Device serial number: %s \n" % strSerialNumber)
            devList.append("USB[" + str(i) + "]" + str(strSerialNumber))

    return deviceList, devList, tlayerType


# ch:打开相机 | en:open device
def open_device(deviceList, obj_cam_operation, b_is_run, nOpenDevSuccess, devList):
    # Counter of how many cameras have been opened
    nOpenDevSuccess = 0

    if True == b_is_run:
        print('Camera is Running!')
        return

    obj_cam_operation = []

    for i in range(0, deviceList.nDeviceNum):
        camObj = MvCamera()  # Create a camera operation
        strName = str(devList[i])

        # Creates a list with different Camera Operation objects
        obj_cam_operation.append(CameraOperation(camObj, deviceList, i))

        # Returns 0 if the camera has been opened
        ret = obj_cam_operation[nOpenDevSuccess].Open_device()

        # If camera has been opened remove it from the Camera Operation objects list and try again with
        # the other cameras
        if ret != 0:
            obj_cam_operation.pop()
            continue

        # If camera has been opened print the camera's information and increment the counter
        else:
            print("Opened: " + str(devList[i]))
            nOpenDevSuccess = nOpenDevSuccess + 1
            model_val = 'continuous'

        # Max amount of cameras to be opened is 4
        if nOpenDevSuccess == 4:
            b_is_run = True
            break

    print("\nAmount of open devices = ", nOpenDevSuccess, "\n")

    return deviceList, obj_cam_operation, b_is_run, nOpenDevSuccess, devList


# ch:开始取流 | en:Start grab image
def start_grabbing(obj_cam_operation, nOpenDevSuccess, lock, barrier, queue):
    ret = 0
    for i in range(0, nOpenDevSuccess):
        start = time.time()
        ret = obj_cam_operation[i].Start_grabbing(i, lock, barrier, queue)
        if ret != 0:
            print('Error: Camera: ' + str(i) + ', start grabbing fail! ret = ' + To_hex_str(ret))
    return obj_cam_operation, nOpenDevSuccess


# ch:停止取流 | en:Stop grab image
def stop_grabbing(nOpenDevSuccess, obj_cam_operation):
    for i in range(0, nOpenDevSuccess):
        ret = obj_cam_operation[i].Stop_grabbing()
        if 0 != ret:
            print('Error: Camera:' + str(i) + ', stop grabbing fail! ret = ' + To_hex_str(ret))
    return nOpenDevSuccess, obj_cam_operation


# ch:关闭设备 | Close device
def close_device(b_is_run, obj_cam_operation, nOpenDevSuccess):
    for i in range(0, nOpenDevSuccess):
        ret = obj_cam_operation[i].Close_device()
        if 0 != ret:
            print('Error: Camera:' + str(i) + ', close device fail! ret = ' + To_hex_str(ret))
            b_is_run = True
            return b_is_run, obj_cam_operation, nOpenDevSuccess
    b_is_run = False
    return b_is_run, obj_cam_operation, nOpenDevSuccess


# ch:设置触发模式 | en:set trigger mode
def set_triggermode(obj_cam_operation, nOpenDevSuccess, model_val):
    strMode = model_val
    for i in range(0, nOpenDevSuccess):
        ret = obj_cam_operation[i].Set_trigger_mode(strMode)
        if 0 != ret:
            print('Error: Camera:' + str(i) + ', set triggersource fail! ret = ' + To_hex_str(ret))
    return obj_cam_operation, nOpenDevSuccess


# ch:设置触发命令 | en:set trigger software
def trigger_once(triggercheck_val, obj_cam_operation, nOpenDevSuccess):
    nCommand = triggercheck_val
    for i in range(0, nOpenDevSuccess):
        ret = obj_cam_operation[i].Trigger_once(nCommand)
        if 0 != ret:
            print('Error: Camera:' + str(i) + ', set triggersoftware fail! ret = ' + To_hex_str(ret))
    return triggercheck_val, obj_cam_operation, nOpenDevSuccess


def get_parameter(obj_cam_operation, nOpenDevSuccess, devList):  # Get frame rate, exposure time and gain for camera
    for i in range(0, nOpenDevSuccess):
        ret = obj_cam_operation[i].Get_parameter()
        if 0 != ret:
            print('Error: camera' + str(i) + 'get parameter fail! ret = ' + To_hex_str(ret))
        print(f'Parameters for camera {str(devList[i])}:')
        print(f'Frame rate: {obj_cam_operation[i].frame_rate}')
        print(f'Exposure time: {obj_cam_operation[i].exposure_time}')
        print(f'Gain: {round(obj_cam_operation[i].gain,1)} \n')

def set_parameter(obj_cam_operation, nOpenDevSuccess, exposure_time, gain, frame_rate):  # Set each camera parameters
    for i in range(0, nOpenDevSuccess):
        obj_cam_operation[i].exposure_time = exposure_time
        obj_cam_operation[i].gain = gain
        obj_cam_operation[i].frame_rate = frame_rate
        ret = obj_cam_operation[i].Set_parameter(obj_cam_operation[i].frame_rate,
                                                 obj_cam_operation[i].exposure_time, obj_cam_operation[i].gain)
        if 0 != ret:
            print('Error: camera' + str(i) + 'set parameter fail!')

    return obj_cam_operation, nOpenDevSuccess


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
    frame_undistorted_l = cv2.remap(frame_left, stereo_map_left_x, stereo_map_left_y, cv2.INTER_LANCZOS4,
                                    cv2.BORDER_CONSTANT, 0)
    frame_undistorted_r = cv2.remap(frame_right, stereo_map_right_x, stereo_map_right_y, cv2.INTER_LANCZOS4,
                                    cv2.BORDER_CONSTANT, 0)

    return frame_undistorted_l, frame_undistorted_r, P1, P2


def get_imagepoints(result_left, result_right):
    # Get the center of the bounding boxes for both frames
    df_left = result_left.pandas().xyxy[0].to_numpy()[0]
    x_min_l, y_min_l, x_max_l, y_max_l = df_left[:4]
    df_right = result_right.pandas().xyxy[0].to_numpy()[0]
    x_min_r, y_min_r, x_max_r, y_max_r = df_right[:4]

    center_x_left = int(x_min_l + (x_max_l - x_min_l) / 2)
    center_y_left = int(y_min_l + (y_max_l - y_min_l) / 2)
    width_left = int(x_max_l - x_min_l)
    height_left = int(y_max_l - y_min_l)

    center_x_right = int(x_min_r + (x_max_r - x_min_r) / 2)
    center_y_right = int(y_min_r + (y_max_r - y_min_r) / 2)
    width_right = int(x_max_r - x_min_r)
    height_right = int(y_max_r - y_min_r)

    return center_x_left, center_y_left, center_x_right, center_y_right, width_left, height_left, width_right, height_right


def resize_dispwind(img_shape):
    w, h = img_shape
    h1 = int(w / 4)
    w1 = int(h / 4)

    cv2.namedWindow("frame_left", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("frame_left", w1, h1)

    cv2.namedWindow("frame_right", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("frame_right", w1, h1)


if __name__ == "__main__":
    # Path to the data folder
    data_path = 'C:/Users/nicgr/Documents/GitHub/BachelorThesis/data/'

    # Rotation and Translation Matrix which are computed in the Stereo_Calibration script
    R = np.load(data_path + 'Calibration/Camera_extrinsics/rotation.npy')
    T = np.load(data_path + 'Calibration/Camera_extrinsics/translation.npy')

    # Camera intrinsics for both cameras
    mtx_left = np.load(data_path + 'Calibration/Camera_intrinsics/mtx_left.npy')
    dist_left = np.load(data_path + 'Calibration/Camera_intrinsics/dist_left.npy')
    mtx_right = np.load(data_path + 'Calibration/Camera_intrinsics/mtx_right.npy')
    dist_right = np.load(data_path + 'Calibration/Camera_intrinsics/dist_right.npy')

    # RT matrix for the left camera is identity.
    RT1 = np.concatenate([np.eye(3), [[0], [0], [0]]], axis=-1)
    P1 = mtx_left @ RT1  # projection matrix for C1

    # RT matrix for the right camera is the R and T obtained from stereo calibration.
    RT2 = np.concatenate([R, T], axis=-1)
    P2 = mtx_right @ RT2  # projection matrix for C2

    # Load the yolov5 model which with custom pretrained weights, trained on the blender images
    yolo = torch.hub.load('ultralytics/yolov5', 'custom',
                          path='C:/Users/nicgr/Documents/GitHub/yolov5/runs/train/yolov5s/weights/last.pt',
                          force_reload=True)

    # Set variables for the capturing of the frames of both cameras
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    obj_cam_operation = 0
    b_is_run = False
    nOpenDevSuccess = 0
    devList = []
    model_val = "triggermode" # should be either "continuous" or "triggermode"
    triggercheck_val = 1
    exposure_time = 15000.0
    gain = 2.0
    frame_rate = 60.0

    # Create barriers, locks and queue to communicate between different threads
    barrier = threading.Barrier(3)
    lock = threading.Lock()
    queue = queue.Queue()

    # Define the names of the frames
    frame_left = None
    frame_right = None

    # Enumerate all cameras and get their information
    deviceList, devList, tlayerType = enum_devices(deviceList, devList, tlayerType)

    # Open the camera so that it is ready to start filming
    deviceList, obj_cam_operation, b_is_run, nOpenDevSuccess, devList = open_device(deviceList, obj_cam_operation,
                                                                                    b_is_run, nOpenDevSuccess, devList)

    # Set the mode of grabbing frames to triggermode, this means that every time the "trigger_once" function is called
    # it will grab a new frame
    obj_cam_operation, nOpenDevSuccess = set_triggermode(obj_cam_operation, nOpenDevSuccess, model_val)

    # Set the parameters of the camera to change the brightness etc.
    obj_cam_operation, nOpenDevSuccess = set_parameter(obj_cam_operation, nOpenDevSuccess, exposure_time, gain, frame_rate)
    get_parameter(obj_cam_operation, nOpenDevSuccess, devList)

    # Start the grabbing threads
    obj_cam_operation, nOpenDevSuccess = start_grabbing(obj_cam_operation, nOpenDevSuccess, lock, barrier, queue)

    # Resize the display windows so that they don't cover the whole screen
    img_size = (2048, 2448)
    resize_dispwind(img_size)

    # Counters to calculate fps
    i = 1
    start = time.time()

    # Start grabbing images and process them
    while True:
        # grab one frame for both cameras (threads) if the camera is in triggermode (if model_val == "triggermode")
        triggercheck_val, obj_cam_operation, nOpenDevSuccess = trigger_once(triggercheck_val, obj_cam_operation,
                                                                            nOpenDevSuccess)

        # Wait until all threads have grabbed a frame and put it into the queue
        barrier.wait()

        # Get both frames from the queue and make sure that no other thread inputs something new into the queue
        with lock:
            for k in range(2):
                ind = queue.get()
                image = queue.get()

                if ind == "left":
                    frame_left = image
                else:
                    frame_right = image

        # Get the framesize for both frames (since its the same camera we only need one)
        img_size = frame_left.shape[:2]

        # frame_undistorted_left, frame_undistorted_right, P1, P2 = undistort_rectify_frames(mtx_left, dist_left, mtx_right,
        #                                                                                    dist_right, img_size, R, T,
        #                                                                                    frame_left, frame_right)

        # Feed the frames to the yolov5s network to detect the objects
        result_left = yolo(frame_left)
        result_right = yolo(frame_right)

        # result_left = yolo(frame_undistorted_left)
        # result_right = yolo(frame_undistorted_right)

        # If the object has not been detected in both frames, show the frames and restart the while loop
        if result_left.pred[0].size()[0] == 0 or result_right.pred[0].size()[0] == 0:
            # Show the left and right frame
            cv2.imshow("frame_left", frame_left)
            cv2.imshow("frame_right", frame_right)

            # If the q Key is pressed stop the recording and print out the frames per second
            if cv2.waitKey(1) == ord('q'):
                with lock:
                    print("FPS = ", round(i / (time.time() - start), 1))
                break
            i += 1
            continue

        # If the object has been detected in both frames compute the center points of the boundingboxes
        center_x_l, center_y_l, center_x_r, center_y_r, width_l, height_l, width_r, height_r = get_imagepoints(result_left, result_right)

        # Triangulate the center of the bounding box
        points3d = cv2.triangulatePoints(P1, P2, (center_x_l, center_y_l), (center_x_r, center_y_r))

        # Calculate the distance form the left camera coordinate system to the bounding box center
        x_distance = (points3d[0] / points3d[3])[0]
        y_distance = (points3d[1] / points3d[3])[0]
        z_distance = (points3d[2] / points3d[3])[0]
        # depth = math.sqrt(x_distance*x_distance + y_distance*y_distance + z_distance*z_distance)
        #
        # print(f'Distance form the camera to the bounding box center: {round(depth, 3)} meters')

        # Draw a circle on the bounding box centers
        frame_left = np.squeeze(result_left.render())
        frame_left = cv2.circle(frame_left, (center_x_l, center_y_l), 10, (0, 0, 256), -1)
        cv2.putText(frame_left, f'X: {round(x_distance, 3)}',
                    (center_x_l - int(width_l / 2), center_y_l + int(height_l / 2) + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        cv2.putText(frame_left,
                    f'Y: {round(y_distance, 3)}',
                    (center_x_l - int(width_l / 2), center_y_l + int(height_l / 2) + 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        cv2.putText(frame_left,
                    f'Z: {round(z_distance, 3)}',
                    (center_x_l - int(width_l / 2), center_y_l + int(height_l / 2) + 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)

        frame_right = np.squeeze(result_right.render())
        frame_right = cv2.circle(frame_right, (center_x_r, center_y_r), 10, (0, 0, 256), -1)
        cv2.putText(frame_right, f'X: {round(x_distance, 3)}',
                    (center_x_r - int(width_r / 2), center_y_r + int(height_r / 2) + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        cv2.putText(frame_right,
                    f'Y: {round(y_distance, 3)}',
                    (center_x_r - int(width_r / 2), center_y_r + int(height_r / 2) + 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        cv2.putText(frame_right,
                    f'Z: {round(z_distance, 3)}',
                    (center_x_r - int(width_r / 2), center_y_r + int(height_r / 2) + 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)

        cv2.imshow("frame_left", frame_left)
        cv2.imshow("frame_right", frame_right)

        if cv2.waitKey(1) == ord('q'):
            with lock:
                print("FPS = ", round(i / (time.time() - start), 1))
            break
        i += 1

    nOpenDevSuccess, obj_cam_operation = stop_grabbing(nOpenDevSuccess, obj_cam_operation)
    b_is_run, obj_cam_operation, nOpenDevSuccess = close_device(b_is_run, obj_cam_operation, nOpenDevSuccess)
    cv2.destroyAllWindows()
