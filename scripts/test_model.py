from pathlib import Path
from src.gesture_classifier import GestureClassifier
ROOT=Path(__file__).resolve().parent.parent
if __name__=='__main__':
    m=GestureClassifier(ROOT/'models/yolox_nano.onnx',ROOT/'models/labels.csv')
    print('Model loaded, model inputs:',[(x.name,x.shape) for x in m.session.get_inputs()])
    print('Model outputs:',[(x.name,x.shape) for x in m.session.get_outputs()])
    print('This tests loading, NOT live gesture accuracy.')
