import pandas as pd
import cv2

data = pd.read_csv('data/yolo.txt',delimiter=" ", header = None)
x1,y1,x2,y2 = data[0][3], data[1][3],data[2][3], data[3][3]
print(data)


#Loading image:
img = cv2.imread('data/artificial_images/car_000002_right.png', -1)
img = cv2.resize(img,(0,0), fx=0.5, fy=0.5)

x1 = int(x1 * img.shape[1])
x2 = int(x2 * img.shape[1])
y1 = int((1-y1) * img.shape[0])
y2 = int((1-y2) * img.shape[0])
print(x1, y1, x2 ,y2)

#draw rectangles:
img = cv2.rectangle(img, (x1,y1), (x2,y2), (255, 0, 0), 5)

cv2.imshow('frame', img)
cv2.waitKey(0)
cv2.destroyAllWindows()