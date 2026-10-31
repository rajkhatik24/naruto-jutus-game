"""CPU YOLOX-Nano ONNX inference; matching original upstream image preprocessing."""
from pathlib import Path
import csv
import numpy as np
import cv2

NORMALIZED = {'Ushi(Ox)':'ox','U(Hare)':'hare','Saru(Monkey)':'monkey'}

class GestureClassifier:
    def __init__(self, model_path, labels_path, confidence=0.65):
        import onnxruntime as ort
        if not Path(model_path).is_file():
            raise FileNotFoundError(f'Missing model: {model_path}. Run python scripts/setup_model.py')
        self.session=ort.InferenceSession(str(model_path),providers=['CPUExecutionProvider'])
        self.input_name=self.session.get_inputs()[0].name
        with open(labels_path,encoding='utf-8-sig',newline='') as f:
            self.labels=[r[0] for r in csv.reader(f)]
        self.confidence=confidence
        self.size=(416,416)
        self.grids,self.strides=self._grids()

    def _grids(self):
        grids=[]; strides=[]
        for s in (8,16,32):
            h,w=416//s,416//s
            xx,yy=np.meshgrid(np.arange(w),np.arange(h))
            grids.append(np.stack((xx,yy),axis=-1).reshape(-1,2))
            strides.append(np.full((h*w,1),s))
        return np.concatenate(grids).astype(np.float32),np.concatenate(strides).astype(np.float32)

    def predict(self, frame):
        h,w=frame.shape[:2]
        ratio=min(416/h,416/w)
        resized=cv2.resize(frame,(int(w*ratio),int(h*ratio)))
        padded=np.full((416,416,3),114,np.uint8)
        padded[:resized.shape[0],:resized.shape[1]]=resized
        tensor=np.ascontiguousarray(padded.transpose(2,0,1),dtype=np.float32)[None]
        output=self.session.run(None,{self.input_name:tensor})[0].copy()
        # Upstream checkpoint uses non-decoded YOLOX output. Decode only once.
        if output.ndim!=3 or output.shape[1]!=self.grids.shape[0] or output.shape[2]<6:
            raise ValueError(f'Unexpected YOLOX output shape {output.shape}; expected (1,3549,5+C)')
        output[...,:2]=(output[...,:2]+self.grids)*self.strides
        output[...,2:4]=np.exp(np.clip(output[...,2:4],-20,20))*self.strides
        rows=output[0]
        scores=rows[:,4:5]*rows[:,5:]
        classes=np.argmax(scores,axis=1)
        values=scores[np.arange(len(classes)),classes]
        ix=np.flatnonzero(values>=self.confidence)
        if not len(ix): return None,0.0,[]
        boxes=rows[ix,:4]
        xywh=np.stack(((boxes[:,0]-boxes[:,2]/2)/ratio,(boxes[:,1]-boxes[:,3]/2)/ratio,boxes[:,2]/ratio,boxes[:,3]/ratio),axis=1)
        keep=cv2.dnn.NMSBoxes(xywh.tolist(),values[ix].tolist(),self.confidence,0.45)
        if len(keep)==0:return None,0.0,[]
        detections=[]
        for k in np.asarray(keep).reshape(-1):
            raw=int(classes[ix[k]])+1 # source labels have a leading None row
            name=self.labels[raw] if raw<len(self.labels) else 'Unknown'
            x,y,bw,bh=xywh[k]
            detections.append({'label':NORMALIZED.get(name,name.lower()),'confidence':float(values[ix[k]]),'box':(int(x),int(y),int(x+bw),int(y+bh))})
        detections.sort(key=lambda d:d['confidence'],reverse=True)
        return detections[0]['label'],detections[0]['confidence'],detections
