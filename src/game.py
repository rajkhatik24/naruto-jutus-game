from pathlib import Path
import json,time
import pygame
from src.camera import Camera
from src.gesture_classifier import GestureClassifier
from src.sequence_engine import SequenceEngine
from src.temporal import TemporalFilter
from src.renderer import Renderer
from src.asset_manager import AssetManager
from src.audio_manager import AudioManager
ROOT=Path(__file__).resolve().parent.parent
class Game:
    def __init__(self, demo=False, video=None):
        self.cfg=json.loads((ROOT/'config/settings.json').read_text())
        self.jutsus=json.loads((ROOT/'config/jutsus.json').read_text())['jutsus']
        self.engine=SequenceEngine(self.jutsus,self.cfg['sequence_timeout_seconds'])
        self.filter=TemporalFilter(self.cfg['stable_frames'],self.cfg['neutral_frames'])
        pygame.init()
        flags=pygame.FULLSCREEN if self.cfg.get('fullscreen') else pygame.RESIZABLE
        self.screen=pygame.display.set_mode((self.cfg['window_width'],self.cfg['window_height']),flags)
        pygame.display.set_caption('Shinobi | Jutsu Tracker')
        self.renderer=Renderer(self.screen,AssetManager(ROOT))
        self.audio=AudioManager(self.cfg['volume'],ROOT)
        self.renderer.prepare(self.jutsus[0])
        self.demo=demo;self.video=video
        self.camera=None;self.classifier=None;self.cap=None
        if not demo:
            self.classifier=GestureClassifier(ROOT/'models/yolox_nano.onnx',ROOT/'models/labels.csv',self.cfg['confidence_threshold'])
            if video:
                import cv2
                self.cap=cv2.VideoCapture(video)
                if not self.cap.isOpened():raise RuntimeError(f'Cannot open video: {video}')
            else:self.camera=Camera(self.cfg['camera_index'],self.cfg['camera_width'],self.cfg['camera_height'])
        if demo:
            # Demo keeps keyboard seals but can show the same live camera view.
            try:
                self.camera=Camera(self.cfg['camera_index'],self.cfg['camera_width'],self.cfg['camera_height'])
            except RuntimeError as exc:
                print(f'Demo camera preview unavailable: {exc}. Keys 1/2/3 still work.')
            if self.camera:
                try:
                    self.classifier=GestureClassifier(ROOT/'models/yolox_nano.onnx',ROOT/'models/labels.csv',self.cfg['confidence_threshold'])
                except (OSError,RuntimeError,ValueError,ImportError) as exc:
                    print(f'Demo detection overlay unavailable: {exc}')
        self.active=None;self.activation_at=0;self.status='Show OX to begin';self.progress=[]
    def activate(self,jutsu,now):
        if self.active is not None:return
        self.renderer.prepare(jutsu)
        self.active=jutsu;self.activation_at=now;self.audio.play(jutsu.get('audio'));self.filter.reset()
    def run(self):
        clock=pygame.time.Clock();running=True;detection=None;confidence=0;detections=[];frame=None
        try:
            while running:
                now=time.monotonic()
                for e in pygame.event.get():
                    if e.type==pygame.QUIT or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE):running=False
                    if e.type==pygame.KEYDOWN and e.key==pygame.K_F5 and not self.active:
                        updated=json.loads((ROOT/'config/jutsus.json').read_text())['jutsus']
                        self.jutsus=updated;self.engine=SequenceEngine(updated,self.cfg['sequence_timeout_seconds'])
                        self.renderer.assets.reload();self.renderer.prepare(updated[0]);self.filter.reset();self.progress=[]
                        self.status='Assets reloaded. Show OX to begin'
                    if self.demo and not self.active and e.type==pygame.KEYDOWN and e.key in (pygame.K_1,pygame.K_2,pygame.K_3):
                        sign={pygame.K_1:'ox',pygame.K_2:'hare',pygame.K_3:'monkey'}[e.key]
                        event=self.engine.accept(sign,now);self.progress=list(event.signs)
                        self.status=f'DEMO input: {sign.upper()} / {event.status}'
                        if event.jutsu:self.activate(event.jutsu,now)
                if not self.active:
                    if self.engine.expire(now):self.progress=[];self.status='Sequence expired. Start again.'
                    if self.demo and self.camera:
                        frame=self.camera.read()
                        if frame is not None and self.classifier:
                            detection,confidence,detections=self.classifier.predict(frame)
                    if not self.demo:
                        if self.camera:frame=self.camera.read()
                        else:
                            ok,frame=self.cap.read()
                            if not ok:running=False;continue
                        if frame is not None:
                            detection,confidence,detections=self.classifier.predict(frame)
                            if self.engine.expire(now):self.progress=[];self.status='Sequence expired. Start again.'
                            accepted=self.filter.feed(detection)
                            if accepted:
                                event=self.engine.accept(accepted,now);self.progress=list(event.signs)
                                self.status=f'{accepted.upper()} confirmed / {event.status}'
                                if event.jutsu:self.activate(event.jutsu,now)
                    if not self.active:
                        self.renderer.webcam(frame,detection,confidence,self.progress,self.jutsus[0]['signs'],self.status,detections,demo=self.demo,needs_neutral=not self.filter.armed)
                if self.active:
                    elapsed=now-self.activation_at
                    if elapsed>=self.active.get('duration_seconds',4):
                        self.audio.stop();self.active=None;self.engine.reset();self.filter.reset();self.progress=[];self.status='Jutsu complete! Show OX to start again'
                    else:self.renderer.cinematic(elapsed,self.active)
                pygame.display.flip();clock.tick(60)
        finally:
            if self.camera:self.camera.close()
            if self.cap:self.cap.release()
            self.audio.close();pygame.quit()
