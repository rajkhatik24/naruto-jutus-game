"""Project-relative, reloadable image assets."""
from pathlib import Path
import logging
import pygame

log = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent.parent

class AssetManager:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        self.cache = {}
        self.animation_cache = {}

    def resolve(self, relative, extensions):
        if not relative:
            log.warning('No asset configured')
            return None
        path = self.root / relative
        if path.suffix.lower() not in extensions:
            log.warning('Unsupported asset format: %s (supported: %s)', path, ', '.join(extensions))
            return None
        if not path.is_file():
            # Allow the configured stem with a different supported extension.
            alternatives = sorted(p for p in path.parent.glob(path.stem + '.*')
                                  if p.suffix.lower() in extensions and p.is_file())
            if len(alternatives) == 1:
                path = alternatives[0]
                log.info('Using asset: %s', path)
            else:
                log.warning('Missing asset: %s%s', path, ' (ambiguous alternatives)' if alternatives else '')
                return None
        return path

    def reload(self):
        self.cache.clear()
        self.animation_cache.clear()

    def image(self, relative):
        path = self.resolve(relative, ('.png', '.jpg', '.jpeg'))
        if path is None:
            return None
        stamp = (path.stat().st_mtime_ns, path.stat().st_size)
        cached = self.cache.get(path)
        if cached and cached[0] == stamp:
            return cached[1]
        try:
            image = pygame.image.load(str(path))
            if pygame.display.get_surface() is not None:
                image = image.convert_alpha()
            self.cache[path] = (stamp, image)
            return image
        except (pygame.error, OSError) as exc:
            log.warning('Cannot load image %s: %s', path, exc)
            return None

    def animation(self, relative):
        if not relative:
            return None
        path=self.resolve(relative, ('.gif',))
        if path is None:
            return None
        stamp=(path.stat().st_mtime_ns,path.stat().st_size)
        cached=self.animation_cache.get(path)
        if cached and cached[0]==stamp:
            return cached[1]
        try:
            from PIL import Image
            from src.animations import GifAnimation
            frames=[];durations=[]
            with Image.open(path) as gif:
                for index in range(gif.n_frames):
                    gif.seek(index)
                    rgba=gif.convert('RGBA')
                    surface=pygame.image.fromstring(rgba.tobytes(),rgba.size,'RGBA')
                    if pygame.display.get_surface() is not None:
                        surface=surface.convert_alpha()
                    frames.append(surface)
                    durations.append(max(10,gif.info.get('duration',100))/1000)
            animation=GifAnimation(frames,durations)
            self.animation_cache[path]=(stamp,animation)
            return animation
        except (ImportError,OSError,ValueError,pygame.error) as exc:
            log.warning('Cannot load animation %s: %s; using image/lightning fallback',path,exc)
            return None
