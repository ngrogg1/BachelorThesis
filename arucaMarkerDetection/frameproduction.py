import numpy as np
import cv2


cap = cv2.VideoCapture(0)
 #If "0" is passed as an argument, then it captures the webcam
 #if "'nameoffile'" is passed as an argument, then it captures the videofile
i = 0
while  True:
    ret, frame = cap.read() #returns np array of the image frame in frame, and if the capture worked properly in ret

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('c'):
        cv2.imwrite('Frames/frame' +str(i)+'.jpg', frame)

    if cv2.waitKey(1) == ord('q'):
        break

    i += 1

cap.release()
cv2.destroyAllWindows()