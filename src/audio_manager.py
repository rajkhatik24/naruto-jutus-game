"""Play configured custom audio once; never silently substitute a sound."""
import logging
from src.asset_manager import AssetManager

log = logging.getLogger(__name__)

class AudioManager:
    def __init__(self, volume=0.65, root=None):
        import pygame
        self.pygame = pygame
        self.assets = AssetManager() if root is None else AssetManager(root)
        self.volume = volume
        self.ok = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.set_volume(volume)
            self.ok = True
        except pygame.error as exc:
            log.warning('Audio initialization failed: %s', exc)

    def play(self, path):
        if not self.ok:
            log.warning('Audio unavailable; cannot play %s', path)
            return False
        self.stop()
        asset = self.assets.resolve(path, ('.mp3', '.wav'))
        if asset is None:
            return False
        try:
            self.pygame.mixer.music.load(str(asset))
            self.pygame.mixer.music.set_volume(self.volume)
            self.pygame.mixer.music.play(loops=0)
            return True
        except (self.pygame.error, OSError) as exc:
            log.warning('Cannot play audio %s: %s', asset, exc)
            return False

    def stop(self):
        if self.ok:
            self.pygame.mixer.music.stop()
            self.pygame.mixer.music.unload()

    def close(self):
        if self.ok:
            self.stop()
            self.pygame.mixer.quit()
            self.ok = False
