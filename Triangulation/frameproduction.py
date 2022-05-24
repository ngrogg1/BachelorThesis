# Imports
import cv2

# To generate images of the ChArUco board, load the video file first
cap = cv2.VideoCapture("E:/Camera_BA/Data/MV-CA050-12UC (G88327234)/Video_20220523152216474.avi")

# Set return value to true to start the first iteration of the video file
ret = True

# Iterate over each frame of the video file
while ret:

    # Sets ret to true if the reading of the file was successful (if the video didn't end), and returns a
    # numpy array of the image frame in frame
    ret, frame = cap.read()

    # Shows the captured frame of the video file
    cv2.imshow('frame', frame)

    # If the key 'c' is pressed, it takes a snapshot of the image and saves it in the Frames directory
    if cv2.waitKey(1) == ord('c'):
        cv2.imwrite('Frames/frame' +str(i)+'.jpg', frame)

    # If the key 'q' is pressed, it ends the video capture
    if cv2.waitKey(1) == ord('q'):
        break

# Release the video file and close all windows
cap.release()
cv2.destroyAllWindows()