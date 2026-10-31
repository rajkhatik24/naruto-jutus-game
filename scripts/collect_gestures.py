"""Record opt-in webcam examples; no automatic upload."""
import argparse,time
from pathlib import Path
import cv2
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--count',type=int,default=30)
    a=p.parse_args();output=Path('samples')/a.label;output.mkdir(parents=True,exist_ok=True)
    cap=cv2.VideoCapture(0)
    try:
        for i in range(a.count):
            ok,frame=cap.read()
            if not ok:break
            cv2.imwrite(str(output/f'{time.time_ns()}.jpg'),frame)
            time.sleep(.2)
    finally:cap.release()
