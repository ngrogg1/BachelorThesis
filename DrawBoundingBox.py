import pandas as pd
import cv2


data = pd.read_csv('data/yolo.txt',delimiter=" ", header = None)
x1,y1,w,h = data[0][2], data[1][2], data[2][2], data[3][2]
# x1,y1,w,h = data[0][3], data[1][3], data[2][3], data[3][3]
print(data)

#Loading image:
img = cv2.imread('data/artificial_images/car_000002_left.png', -1)
# img = cv2.imread('data/artificial_images/car_000002_right.png', -1)
img = cv2.resize(img,(0,0), fx=0.5, fy=0.5)

x1 = int(x1 * img.shape[1])
x2 = int(x1 + w * img.shape[1])
y1 = int((1-y1) * img.shape[0])
y2 = int(y1 - h * img.shape[0])
print(x1, y1, x2 ,y2)

#draw rectangles:
img = cv2.rectangle(img, (x1,y1), (x2,y2), (255, 0, 0), 2) #blue

#draw circles:
img = cv2.circle(img, (x1,y1), 5, (0, 0, 255), -1) #red
img = cv2.circle(img, (x2,y2), 5, (0, 255, 0), -1) #green

cv2.imshow('frame', img)
cv2.waitKey(0)
cv2.destroyAllWindows()





# import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle
# from PIL import Image
# x = (x1+x2)/2
# y = (y1+y2)/2
# # Display the image
# img = Image.open('data/artificial_images/car_000002_right.png')
# width, height =img.size
# x = x1 * width
# y = (1-y2) * height
# w = (x2-x1) * width
# h = (y2-y1) * height
# plt.imshow(img)
#
# # Add the patch to the Axes
# plt.gca().add_patch(Rectangle((x,y),w,h,linewidth=1,edgecolor='r',facecolor='none'))
#
# plt.show()