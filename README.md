# Shinobi Jutsu Tracker — Chidori MVP

A CPU-first webcam game: hold **Ox → Hare → Monkey**, relaxing your hands out of the frame between each seal. A real YOLOX-Nano detector recognizes the seals; Chidori then triggers an animated blue lightning reveal and audio. No jutsu-selection menu.

## Windows 11 / Python 3.11

```powershell
cd naruto-jutsu-tracker
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python scripts/setup_model.py
python scripts/test_model.py
python main.py
```

If `py -3.11` is not installed, install Python 3.11 and then use `python -m venv .venv`. Run commands from the project root. Change `camera_index` in `config/settings.json` for a secondary camera. All recognition is offline after downloading dependencies/model.

## Demo / tests

```powershell
python main.py --demo
python -m pytest -q
python scripts/test_camera.py
python main.py --video path\to\handsigns.mp4
```

**Demo mode** works without a model or camera. When available, the webcam fills the window and real model detections supply labeled bounding boxes; activation remains controlled by keys. Press **1**, **2**, **3** to simulate Ox/Hare/Monkey and test the entire visual/audio loop. Demo keyboard input is *not* real classification; normal gameplay requires no keyboard. ESC exits. F5 reloads jutsu configuration and assets. The illustrated guide advances through the required seals. Completing the sequence plays the configured GIF for four seconds, with the custom MP3 playing once, then returns to the camera.

## Real gameplay

Place both hands clearly in the camera, hold each sign for at least 5 processed frames, then move your hands completely out of the camera view for at least 4 processed frames before the next sign. This explicit neutral-state gate prevents a held sign from counting multiple times. A model confidence >= 0.65 is required. HUD shows the chosen detection and confidence, and frames with candidates draw boxes. Bright even lighting and clear backgrounds help. This detector estimates a complete seal bounding box, **not** independent skeletons of both hands.

## Model and rights

Original code/model: https://github.com/Kazuhito00/NARUTO-HandSignDetection (MIT). Model URL: https://raw.githubusercontent.com/Kazuhito00/NARUTO-HandSignDetection/main/model/yolox/yolox_nano.onnx . The original model supports 14 seals and its `labels.csv` includes offset 1 for class indexing. Implemented preprocessing, grid decode and NMS based on upstream `model/yolox/yolox_onnx.py`; model weights are downloaded separately rather than included.

The repo's original training set contains varied sources and model reliability depends on clothing/background. **No webcam performance claims are made** for this package until tested on your machine. If the model download or runtime fails, real recognition is unavailable, not simulated. Recorded-video inference can assist in checking accuracy.

## Media and extensions

The local assets include the user-selected Sasuke image, Chidori audio, anime sign chart, and Chidori GIF. Media source references are recorded in `assets/signs/SOURCES.md` and `assets/effects/SOURCES.md`; these are third-party media, not original project artwork. Asset paths are configured in `config/jutsus.json` and resolved relative to the project root. PNG/JPG/JPEG images, MP3/WAV audio, and timed GIF playback are supported. If the GIF is unavailable, the renderer uses the image/lightning effect; missing audio produces a diagnostic and silence. The game refers to Naruto/Sasuke as fan-art context and is not affiliated with rights holders.

Add jutsu sequences to `config/jutsus.json`; the sequence engine matches prefixes. If sequences share a prefix and one is also a complete jutsu, the engine waits for a longer sequence instead of immediately triggering the shorter one; this can be refined later with a configurable match-finalization delay. Shadow Clone crossed fingers and Rasengan require custom recognition and are NOT implemented. The current renderer is Chidori-specific.

## Practical limitations

- Local verification: ONNX loading and blank-frame inference succeeded; 15 automated tests passed. Live webcam capture was unavailable during validation.
- FPS varies by CPU; this implementation runs capture/inference on the render thread, so slower systems may dip below 20 FPS.
- Moving your hands completely out of frame between seals is required; otherwise the gate will not re-arm.
- Multiple detections are displayed, but only the top scoring seal drives the engine.
- Window resizing is supported; older versions of Pygame can require refresh after resize.
- Only the first MVP jutsu is playable; no training or claims of Shadow Clone/Rasengan are included.
