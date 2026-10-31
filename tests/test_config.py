import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def test_config():
    conf=json.loads((ROOT/'config/settings.json').read_text())
    js=json.loads((ROOT/'config/jutsus.json').read_text())['jutsus']
    assert conf['stable_frames']>0
    assert js[0]['signs']==['ox','hare','monkey']
def test_label_mapping():
    from src.gesture_classifier import NORMALIZED
    assert NORMALIZED['Ushi(Ox)']=='ox'
    assert NORMALIZED['U(Hare)']=='hare'
    assert NORMALIZED['Saru(Monkey)']=='monkey'
