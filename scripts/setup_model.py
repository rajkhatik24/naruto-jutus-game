"""Downloads the third-party pretrained MIT-licensed YOLOX checkpoint."""
from pathlib import Path
from urllib.request import urlretrieve
from urllib.error import URLError
ROOT=Path(__file__).resolve().parent.parent
URL='https://raw.githubusercontent.com/Kazuhito00/NARUTO-HandSignDetection/main/model/yolox/yolox_nano.onnx'
DEST=ROOT/'models/yolox_nano.onnx'
def main():
    if DEST.exists() and DEST.stat().st_size>100000:print(f'Already present: {DEST}');return
    print(f'Downloading {URL}')
    try:
        urlretrieve(URL,DEST)
        if DEST.stat().st_size<100000:raise ValueError('Downloaded model is unexpectedly small')
    except (URLError,OSError,ValueError):
        DEST.unlink(missing_ok=True)
        raise
    print(f'Saved {DEST} ({DEST.stat().st_size/1024/1024:.1f} MB)')
if __name__=='__main__':main()
