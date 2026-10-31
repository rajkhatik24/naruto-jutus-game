"""Time-driven Chidori charge, orbiting sparks and branched lightning."""
import random, math
import pygame

class Lightning:
    def __init__(self):
        self.rng=random.Random(233)

    def draw(self,surface,seconds,center=None):
        w,h=surface.get_size()
        center=center or (int(w*.65),int(h*.45))
        charge=min(1.0,max(.1,seconds/1.1))
        pulse=1+.10*math.sin(seconds*27)
        radius=max(8,int(38*charge*pulse))
        glow=pygame.Surface((w,h),pygame.SRCALPHA)
        for r in range(radius*4,radius,-8):
            alpha=int(7+30*(1-r/(radius*4)))
            pygame.draw.circle(glow,(25,130,255,alpha),center,r)
        surface.blit(glow,(0,0))
        # Fixed time steps make flicker independent of rendering frame rate.
        self.rng.seed(int(seconds*28))
        for i in range(11):
            angle=i*math.tau/11+seconds*1.4
            reach=(70+self.rng.random()*120)*charge
            points=[center]
            for step in range(1,6):
                distance=reach*step/5
                jitter=self.rng.uniform(-15,15)
                points.append((int(center[0]+math.cos(angle)*distance-math.sin(angle)*jitter),
                               int(center[1]+math.sin(angle)*distance+math.cos(angle)*jitter)))
            pygame.draw.lines(surface,(15,70,175),False,points,7)
            pygame.draw.lines(surface,(50,170,255),False,points,3)
            pygame.draw.lines(surface,(205,250,255),False,points,1)
        for i in range(38):
            angle=i*2.4+seconds*(1.4+i%3)
            distance=radius+((i*19+seconds*100)%150)*charge
            point=(int(center[0]+math.cos(angle)*distance),int(center[1]+math.sin(angle)*distance*.7))
            pygame.draw.circle(surface,(110,210,255),point,1+i%3)
        pygame.draw.circle(surface,(65,180,255),center,radius)
        pygame.draw.circle(surface,(175,240,255),center,max(1,int(radius*.72)))
        pygame.draw.circle(surface,(245,255,255),center,max(1,int(radius*.45)))


class GifAnimation:
    """Decoded GIF frames selected by elapsed time, never render frame count."""
    def __init__(self, frames, durations):
        from itertools import accumulate
        if not frames or len(frames) != len(durations):
            raise ValueError('GIF requires frames and matching durations')
        self.frames=frames
        self.ends=list(accumulate(durations))
        self.duration=self.ends[-1]

    def frame_index(self, seconds):
        from bisect import bisect_right
        return min(len(self.frames)-1,bisect_right(self.ends,max(0,seconds)%self.duration))

    def frame(self, seconds):
        return self.frames[self.frame_index(seconds)]
