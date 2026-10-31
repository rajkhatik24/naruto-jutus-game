import cv2
class Camera:
    def __init__(self,index=0,width=960,height=540):
        self.cap=cv2.VideoCapture(index,cv2.CAP_DSHOW if __import__('sys').platform=='win32' else cv2.CAP_ANY)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
        if not self.cap.isOpened():raise RuntimeError('Could not open webcam. Try another camera_index in config/settings.json')
    def read(self):
        ok,frame=self.cap.read()
        return cv2.flip(frame,1) if ok else None
    def close(self):self.cap.release()
