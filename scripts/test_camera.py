import cv2
if __name__=='__main__':
    cap=cv2.VideoCapture(0)
    print('Camera open:',cap.isOpened())
    if cap.isOpened():
        ok,frame=cap.read();print('Frame received:',ok,'shape:',frame.shape if ok else None)
    cap.release()
