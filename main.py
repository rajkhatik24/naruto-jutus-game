import argparse
from src.game import Game
if __name__=='__main__':
    p=argparse.ArgumentParser(description='Naruto-inspired hand-seal arcade game')
    p.add_argument('--demo',action='store_true',help='Test UI without model/camera: press 1,2,3')
    p.add_argument('--video',help='Run real model on prerecorded video instead of webcam')
    a=p.parse_args()
    try:Game(demo=a.demo,video=a.video).run()
    except (OSError,RuntimeError,ValueError) as e:
        print(f'ERROR: {e}')
        raise SystemExit(1)
