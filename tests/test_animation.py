import pygame
import pytest
from src.animations import GifAnimation
from src.asset_manager import AssetManager


def test_variable_frame_timing_and_loop():
    animation=GifAnimation(['first','second','third'],[.1,.2,.4])
    assert animation.frame(0)=='first'
    assert animation.frame(.15)=='second'
    assert animation.frame(.35)=='third'
    assert animation.frame(.75)=='first'
    assert animation.frame(-1)=='first'
    with pytest.raises(ValueError):
        GifAnimation([],[])


def test_actual_gif_and_fallback(tmp_path):
    pygame.init()
    pygame.display.set_mode((640,480))
    try:
        assets=AssetManager()
        animation=assets.animation('assets/effects/chidori_giphy.gif')
        assert len(animation.frames)==12
        assert animation.duration==pytest.approx(1.2)
        assert animation.frame(0).get_size()==(250,188)
        assert animation is assets.animation('assets/effects/chidori_giphy.gif')
        assets.reload()
        assert assets.animation('assets/effects/chidori_giphy.gif') is not animation
        broken=tmp_path/'broken.gif'
        broken.write_bytes(b'not a GIF')
        assert assets.animation(str(broken)) is None
        assert assets.animation(str(tmp_path/'missing.gif')) is None
    finally:
        pygame.quit()
