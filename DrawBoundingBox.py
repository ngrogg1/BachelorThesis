import pandas as pd
import cv2

data = pd.read_csv('data/yolo.txt',delimiter=" ", header = None)
i = 0
k = 0

while i < len(data)/2:
    x_center_l, y_center_l, w1, h1 = data[0][k], data[1][k], data[2][k], data[3][k]
    k += 1
    x_center_r, y_center_r, w2, h2 = data[0][k], data[1][k], data[2][k], data[3][k]
    k += 1

    #Loading image:
    img_l = cv2.imread('data/artificial_images/car_' + f'{str(i + 1).zfill(6)}' + '_left.png', -1)
    img_r = cv2.imread('data/artificial_images/car_' + f'{str(i + 1).zfill(6)}' + '_right.png', -1)
    img_l = cv2.resize(img_l,(0,0), fx=0.5, fy=0.5)
    img_r = cv2.resize(img_r, (0, 0), fx=0.5, fy=0.5)

    x1_l = int((x_center_l - w1/2) * img_l.shape[1])
    x2_l = int(x1_l + w1 * img_l.shape[1])
    y1_l = int((y_center_l + h1/2) * img_l.shape[0])
    y2_l = int(y1_l - h1 * img_l.shape[0])
    print(x1_l, y1_l, x2_l, y2_l)

    x1_r = int((x_center_r - w2/2) * img_r.shape[1])
    x2_r = int(x1_r + w2 * img_r.shape[1])
    y1_r = int((y_center_r + h2/2) * img_r.shape[0])
    y2_r = int(y1_r - h2 * img_r.shape[0])
    print(x1_r, y1_r, x2_r, y2_r)

    # draw rectangles:
    img_l = cv2.rectangle(img_l, (x1_l,y1_l), (x2_l,y2_l), (255, 0, 0), 2) # blue
    img_r = cv2.rectangle(img_r, (x1_r, y1_r), (x2_r, y2_r), (255, 0, 0), 2)  # blue

    # draw center point
    img_l = cv2.circle(img_l, (int(x_center_l * img_l.shape[1]), int(y_center_l * img_l.shape[0])), 4, (0, 0, 255), -1) # red
    img_r = cv2.circle(img_r, (int(x_center_r * img_r.shape[1]), int(y_center_r * img_r.shape[0])), 4, (0, 0, 255), -1) # red

    cv2.imshow('left', img_l)
    cv2.imshow('right', img_r)
    if cv2.waitKey(4000) == ord('q'):
        break
    i +=1
cv2.destroyAllWindows()