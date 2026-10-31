import os
import wave
import threading
import time
from pathlib import Path
from unittest.mock import Mock

import pygame
import pytest

from src.asset_manager import AssetManager
from src.audio_manager import AudioManager
from src.game import Game

@pytest.fixture
def display():
    pygame.init()
    pygame.display.set_mode((640, 480))
    yield
    pygame.quit()

@pytest.mark.parametrize('extension', ['png', 'jpg', 'jpeg'])
def test_image_formats_reload_and_cwd(tmp_path, monkeypatch, display, extension):
    image = pygame.Surface((60, 100), pygame.SRCALPHA)
    image.fill((30, 150, 250, 128))
    path = tmp_path / ('custom.' + extension)
    pygame.image.save(image, str(path))
    assets = AssetManager(tmp_path)
    monkeypatch.chdir(tmp_path.parent)
    loaded = assets.image(path.name)
    assert loaded.get_size() == (60, 100)
    if extension == 'png':
        assert loaded.get_at((0, 0)).a == 128
    assets.reload()
    assert assets.image(path.name) is not loaded
    assert assets.image('absent.png') is None
    assert assets.image('unsupported.gif') is None


def test_wav_playback_and_missing(tmp_path, display):
    path = tmp_path / 'custom.wav'
    with wave.open(str(path), 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(22050)
        output.writeframes(bytes(44100))
    audio = AudioManager(root=tmp_path)
    assert audio.ok
    assert audio.play('custom.wav')
    assert pygame.mixer.music.get_busy()
    assert not audio.play('absent.mp3')
    assert not pygame.mixer.music.get_busy()
    audio.close()


def test_demo_event_loop_and_four_second_return(monkeypatch):
    game = Game(demo=True)
    game.audio.play = Mock(return_value=True)
    calls = []
    original = game.renderer.cinematic
    def render(elapsed, jutsu):
        calls.append(elapsed)
        original(elapsed, jutsu)
    game.renderer.cinematic = render
    def send_keys():
        time.sleep(.15)
        for key in (pygame.K_1, pygame.K_2, pygame.K_3):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
            time.sleep(.08)
        # Ignore additional complete input while cinematic is running.
        for key in (pygame.K_1, pygame.K_2, pygame.K_3):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
        time.sleep(4.25)
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    thread = threading.Thread(target=send_keys)
    thread.start()
    game.run()
    thread.join()
    assert game.audio.play.call_count == 1
    assert calls and 3.8 < max(calls) < 4.1
    assert game.active is None
    assert game.progress == []
