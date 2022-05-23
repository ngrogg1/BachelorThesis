
import cv2
import numpy as np
import os


aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
board = cv2.aruco.CharucoBoard_create(5, 7, 0.03, 0.0175, aruco_dict)

allCorners = []
allIds = []
decimator = 0

images = os.listdir('Frames')

for fname in images:

    img = cv2.imread(os.path.join('Frames',fname))
    #img = cv2.resize(img, (1920,1080))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = cv2.aruco.detectMarkers(gray,aruco_dict)

    if len(res[0])>0:
        res2 = cv2.aruco.interpolateCornersCharuco(res[0],res[1],gray,board)
        if res2[1] is not None and res2[2] is not None: # and len(res2[1])>10 and decimator%3==0 and res2[0] > 12:
            print(res2[2])
            allCorners.append(res2[1])
            allIds.append(res2[2])

            cv2.aruco.drawDetectedMarkers(gray,res[0],res[1])
            #plt.figure()
            #plt.imshow(gray)
            #plt.show()
            cv2.imwrite('CalibrationOutput/' + fname, gray)



    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    decimator+=1

imsize = gray.shape


_, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(allCorners,allIds,board,imsize,None,None)

print(cameraMatrix)
print(distCoeffs)

np.save('CalibrationOutput/mtx.npy', cameraMatrix)
np.save('CalibrationOutput/dist.npy',distCoeffs)
cv2.destroyAllWindows()