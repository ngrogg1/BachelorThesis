import pandas as pd
import cv2

data = pd.read_csv('data/yolo.txt',delimiter=" ", header = None)
i = 0
k = 0

while i < len(data)/2:
    x1l, y1l, w1, h1 = data[0][k], data[1][k], data[2][k], data[3][k]
    k += 1
    x1r, y1r, w2, h2 = data[0][k], data[1][k], data[2][k], data[3][k]
    k += 1

    #Loading image:
    img_l = cv2.imread('data/artificial_images/car_' + f'{str(i + 1).zfill(6)}' + '_left.png', -1)
    img_r = cv2.imread('data/artificial_images/car_' + f'{str(i + 1).zfill(6)}' + '_right.png', -1)
    img_l = cv2.resize(img_l,(0,0), fx=0.5, fy=0.5)
    img_r = cv2.resize(img_r, (0, 0), fx=0.5, fy=0.5)

    x1l = int(x1l * img_l.shape[1])
    x2l = int(x1l + w1 * img_l.shape[1])
    y1l = int((1-y1l) * img_l.shape[0])
    y2l = int(y1l - h1 * img_l.shape[0])
    print(x1l, y1l, x2l, y2l)

    x1r = int(x1r * img_r.shape[1])
    x2r = int(x1r + w2 * img_r.shape[1])
    y1r = int((1 - y1r) * img_r.shape[0])
    y2r = int(y1r - h2 * img_r.shape[0])
    print(x1r, y1r, x2r, y2r)

    #draw rectangles:
    img_l = cv2.rectangle(img_l, (x1l,y1l), (x2l,y2l), (255, 0, 0), 2) #blue
    img_r = cv2.rectangle(img_r, (x1r, y1r), (x2r, y2r), (255, 0, 0), 2)  # blue

    cv2.imshow('left', img_l)
    cv2.imshow('right', img_r)
    if cv2.waitKey(4000) == ord('q'):
        break
    i +=1
cv2.destroyAllWindows()