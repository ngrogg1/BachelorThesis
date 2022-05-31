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

import cv2

sys.path.append("C:/Users/Nic/Documents/GitHub/BachelorThesis/Triangulation/MvImport")

from MvCameraControl_class import *
from CamOperation_class import *
from PIL import Image, ImageTk


def To_hex_str(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2**32
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

    print("Found %d devices!" % deviceList.nDeviceNum)

    devList = []
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents

        # Print USB device information
        if mvcc_dev_info.nTLayerType == MV_USB_DEVICE:  # we use usb
            print("\nu3v device: [%d]" % i)
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
            print("Device serial number: %s" % strSerialNumber)
            devList.append("USB[" + str(i) + "]" + str(strSerialNumber))

    return deviceList, devList, tlayerType

# ch:打开相机 | en:open device
def open_device(deviceList, obj_cam_operation, b_is_run, nOpenDevSuccess, devList):
    # global deviceList
    # global obj_cam_operation
    # global b_is_run
    # global nOpenDevSuccess
    # global devList

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
            print(str(devList[i]))
            nOpenDevSuccess = nOpenDevSuccess + 1
            model_val = 'continuous'

        # Max amount of cameras to be opened is 4
        if nOpenDevSuccess == 4:
            b_is_run = True
            break

        print("Amount of open devices = ", nOpenDevSuccess)

    return deviceList, obj_cam_operation, b_is_run, nOpenDevSuccess, devList

# ch:开始取流 | en:Start grab image
def start_grabbing(obj_cam_operation, nOpenDevSuccess, lock, barrier):
    # global obj_cam_operation
    # global nOpenDevSuccess
    ret = 0
    for i in range(0, nOpenDevSuccess):
        start = time.time()
        ret = obj_cam_operation[i].Start_grabbing(i, lock, barrier)
        if ret != 0:
            print('Error: Camera: ' + str(i) + ', start grabbing fail! ret = ' + To_hex_str(ret))
    return obj_cam_operation, nOpenDevSuccess

# ch:停止取流 | en:Stop grab image
def stop_grabbing(nOpenDevSuccess, obj_cam_operation):
    # global nOpenDevSuccess
    # global obj_cam_operation
    for i in range(0, nOpenDevSuccess):
        ret = obj_cam_operation[i].Stop_grabbing()
        if 0 != ret:
            print('Error: Camera:' + str(i) + ', stop grabbing fail! ret = ' + To_hex_str(ret))
    return nOpenDevSuccess, obj_cam_operation

# ch:关闭设备 | Close device
def close_device(b_is_run, obj_cam_operation, nOpenDevSuccess):
    # global b_is_run
    # global obj_cam_operation
    # global nOpenDevSuccess
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
    # global obj_cam_operation
    # global nOpenDevSuccess
    strMode = model_val
    for i in range(0, nOpenDevSuccess):
        ret = obj_cam_operation[i].Set_trigger_mode(strMode)
        if 0 != ret:
            print('Error: Camera:' + str(i) + ', set triggersource fail! ret = ' + To_hex_str(ret))
    return obj_cam_operation, nOpenDevSuccess

# ch:设置触发命令 | en:set trigger software
def trigger_once(triggercheck_val, obj_cam_operation, nOpenDevSuccess):
    # global triggercheck_val
    # global obj_cam_operation
    # global nOpenDevSuccess
    nCommand = triggercheck_val
    for i in range(0, nOpenDevSuccess):
        ret = obj_cam_operation[i].Trigger_once(nCommand)
        if 0 != ret:
            print('Error: Camera:' + str(i) + ', set triggersoftware fail! ret = ' + To_hex_str(ret))
    return triggercheck_val, obj_cam_operation, nOpenDevSuccess

# def get_parameter():  # Get frame rate, exposure time and gain for camera
#     global obj_cam_operation
#     global nOpenDevSuccess
#     for i in range(0, nOpenDevSuccess):
#         ret = obj_cam_operation[i].Get_parameter()
#         if 0 != ret:
#             tkinter.messagebox.showerror('show error',
#                                          'camera' + str(i) + 'get parameter fail!ret = ' + To_hex_str(ret))
#         text_frame_rate.delete(1.0, tk.END)
#         text_frame_rate.insert(1.0, obj_cam_operation[i].frame_rate)
#         text_exposure_time.delete(1.0, tk.END)
#         text_exposure_time.insert(1.0, obj_cam_operation[i].exposure_time)
#         text_gain.delete(1.0, tk.END)
#         text_gain.insert(1.0, obj_cam_operation[i].gain)
#
# def set_parameter():  # Set each camera parameters
#     global obj_cam_operation
#     global nOpenDevSuccess
#     for i in range(0, nOpenDevSuccess):
#         obj_cam_operation[i].exposure_time = text_exposure_time.get(1.0, tk.END)
#         obj_cam_operation[i].exposure_time = obj_cam_operation[i].exposure_time.rstrip("\n")
#         obj_cam_operation[i].gain = text_gain.get(1.0, tk.END)
#         obj_cam_operation[i].gain = obj_cam_operation[i].gain.rstrip("\n")
#         obj_cam_operation[i].frame_rate = text_frame_rate.get(1.0, tk.END)
#         obj_cam_operation[i].frame_rate = obj_cam_operation[i].frame_rate.rstrip("\n")
#         ret = obj_cam_operation[i].Set_parameter(obj_cam_operation[i].frame_rate,
#                                                  obj_cam_operation[i].exposure_time, obj_cam_operation[i].gain)
#         if 0 != ret:
#             tkinter.messagebox.showerror('show error', 'camera' + str(i) + 'set parameter fail!')

if __name__ == "__main__":
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    obj_cam_operation = 0
    b_is_run = False
    nOpenDevSuccess = 0
    devList = []
    model_val = "triggermode"
    triggercheck_val = 1

    barrier = threading.Barrier(3)
    lock = threading.Lock()
    deviceList, devList, tlayerType = enum_devices(deviceList, devList, tlayerType)
    deviceList, obj_cam_operation, b_is_run, nOpenDevSuccess, devList = open_device(deviceList, obj_cam_operation, b_is_run, nOpenDevSuccess, devList)
    obj_cam_operation, nOpenDevSuccess = set_triggermode(obj_cam_operation, nOpenDevSuccess, model_val)
    obj_cam_operation, nOpenDevSuccess = start_grabbing(obj_cam_operation, nOpenDevSuccess, lock, barrier)
    i = 1
    start = time.time()
    while True:

        triggercheck_val, obj_cam_operation, nOpenDevSuccess = trigger_once(triggercheck_val, obj_cam_operation,
                                                                            nOpenDevSuccess)

        barrier.wait()

        frame_left = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/live/frame_left.jpg', -1)
        frame_right = cv2.imread('C:/Users/Nic/Documents/GitHub/BachelorThesis/data/live/frame_right.jpg', -1)
        frame_left = cv2.resize(frame_left, (0,0), fx=0.25, fy=0.25)
        frame_right = cv2.resize(frame_right, (0,0), fx=0.25, fy=0.25)

        cv2.imshow("frame_left", frame_left)
        cv2.imshow("frame_right", frame_right)
        if cv2.waitKey(1) == ord('q'):
            with lock:
                print("FPS = ", round(i/(time.time()-start),1))
            break
        i += 1
    nOpenDevSuccess, obj_cam_operation = stop_grabbing(nOpenDevSuccess, obj_cam_operation)
    b_is_run, obj_cam_operation, nOpenDevSuccess = close_device(b_is_run, obj_cam_operation, nOpenDevSuccess)

