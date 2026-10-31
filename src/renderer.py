import math
import pygame
from src.animations import Lightning
class Renderer:
    def __init__(self,screen,assets):
        self.screen=screen;self.assets=assets;self.lightning=Lightning()
        self.font=pygame.font.SysFont('arial',29,bold=True)
        self.small=pygame.font.SysFont('consolas',19)
        self.big=pygame.font.SysFont('arial',96,bold=True)
        self.guide_images={}
        self.guide_scaled={}
        self.animation=None
        self.animation_scaled={}
        self.art=None
        self.scaled_art=None
        self.scaled_key=None
    def prepare(self, jutsu):
        self.animation=self.assets.animation(jutsu.get('animation'))
        self.animation_scaled.clear()
        self.art = self.assets.image(jutsu.get('image'))
        if self.art is not None:
            self.art = self._clear_border_background(self.art)
        self.scaled_key = None
        # The user-selected anime chart is a 4-column, 3-row sprite atlas.
        chart=self.assets.image('assets/signs/reddit_hand_signs.jpeg')
        cells={'ox':(0,2),'hare':(2,2),'monkey':(2,1)}
        self.guide_images={}
        for sign,(column,row) in cells.items():
            if chart is not None:
                cw,ch=chart.get_width()//4,chart.get_height()//3
                self.guide_images[sign]=chart.subsurface((column*cw,row*ch,cw,ch)).copy()
            else:
                self.guide_images[sign]=self.assets.image(f'assets/signs/{sign}.jpg')
        self.guide_scaled.clear()

    @staticmethod
    def _clear_border_background(image):
        """Remove only border-connected bright neutral pixels from opaque art.

        Some downloaded 'transparent' PNGs contain an actual checkerboard.
        Work on a copy, leaving the source file and enclosed highlights intact.
        """
        import cv2
        import numpy as np
        rgb = pygame.surfarray.array3d(image).astype(np.int16)
        alpha = pygame.surfarray.array_alpha(image)
        # Genuine transparent artwork already has a usable alpha channel.
        if np.any(alpha == 0):
            return image
        neutral = ((rgb.max(axis=2)-rgb.min(axis=2) <= 16)
                   & (rgb.min(axis=2) >= 175)).astype(np.uint8)
        # A solid light border is the signature of the supplied checkerboard.
        border = np.concatenate((neutral[0],neutral[-1],neutral[:,0],neutral[:,-1]))
        if border.mean() < .9:
            return image
        count, labels = cv2.connectedComponents(neutral, connectivity=4)
        edge_labels = np.unique(np.concatenate((labels[0],labels[-1],labels[:,0],labels[:,-1])))
        remove = np.isin(labels, edge_labels[edge_labels != 0])
        result = image.copy().convert_alpha()
        pixels = pygame.surfarray.pixels_alpha(result)
        pixels[remove] = 0
        del pixels
        return result

    def text(self,s,x,y,color=(230,242,255),font=None):
        self.screen.blit((font or self.font).render(s,True,color),(x,y))
    def webcam(self,frame,label,confidence,progress,target,status,detections=None,demo=False,needs_neutral=False):
        import cv2
        import numpy as np
        w,h=self.screen.get_size()
        self.screen.fill((0,0,0))
        if frame is not None:
            fh,fw=frame.shape[:2]
            # Fill the entire window, preserving camera aspect ratio.
            sc=max(w/fw,h/fh)
            dw,dh=max(w,round(fw*sc)),max(h,round(fh*sc))
            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            pic=pygame.image.frombuffer(np.ascontiguousarray(rgb).tobytes(),(fw,fh),'RGB')
            pic=pygame.transform.smoothscale(pic,(dw,dh))
            ox,oy=(w-dw)//2,(h-dh)//2
            self.screen.blit(pic,(ox,oy))
            for detection in detections or []:
                rect=self.detection_rect(detection['box'],(fw,fh),(w,h))
                if rect.width<2 or rect.height<2:
                    continue
                next_sign=target[min(len(progress),len(target)-1)] if target else None
                color=(100,245,170) if detection['label']==next_sign else (255,200,90)
                pygame.draw.rect(self.screen,color,rect,3,border_radius=8)
                caption=self.small.render(f"{detection['label'].upper()}  {detection['confidence']:.0%}",True,(10,18,24))
                tag=caption.get_rect(topleft=(min(rect.x,max(0,w-caption.get_width()-12)),max(55,rect.y-29)))
                pygame.draw.rect(self.screen,color,tag.inflate(12,6),border_radius=4)
                self.screen.blit(caption,tag)
        else:
            self.text('Camera unavailable',24,h//2,(240,240,240))
            self.text('Connect a webcam for the live view.',24,h//2+40,font=self.small)
        # Small translucent overlays leave the live image as the main screen.
        shade=pygame.Surface((w,54),pygame.SRCALPHA);shade.fill((0,0,0,115))
        self.screen.blit(shade,(0,0))
        self.text('CHIDORI  /  '+('KEY DEMO' if demo else 'LIVE'),20,16,(230,246,255),self.small)
        if not demo:
            self.text(f'{label or "NO SEAL"}  {confidence:.0%}',max(20,w-230),16,font=self.small)
        footer=pygame.Surface((w,65),pygame.SRCALPHA);footer.fill((0,0,0,135))
        self.screen.blit(footer,(0,h-65))
        sequence='  >  '.join(('['+sign.upper()+']') if i<len(progress) else sign.upper() for i,sign in enumerate(target))
        self.text(sequence,20,h-59,(145,230,255),self.small)
        self.text(status,20,h-31,(235,240,245),self.small)
        self.text('ESC quit | F5 reload',max(20,w-245),h-59,font=self.small)
        self.sign_guide(progress,target,demo,needs_neutral)

    @staticmethod
    def detection_rect(box, frame_size, screen_size):
        """Use exactly the same cover scale and centre crop as the camera."""
        fw,fh=frame_size;w,h=screen_size
        scale=max(w/fw,h/fh)
        dw,dh=max(w,round(fw*scale)),max(h,round(fh*scale))
        ox,oy=(w-dw)//2,(h-dh)//2
        x1,y1,x2,y2=box
        left,top=round(ox+x1*dw/fw),round(oy+y1*dh/fh)
        right,bottom=round(ox+x2*dw/fw),round(oy+y2*dh/fh)
        return pygame.Rect(left,top,max(0,right-left),max(0,bottom-top)).clip(pygame.Rect(0,0,w,h))

    def sign_guide(self, progress, target, demo=False, needs_neutral=False):
        if not target:
            return
        index=min(len(progress),len(target)-1)
        sign=target[index]
        w,h=self.screen.get_size()
        width=min(300,max(220,w//3))
        photo_height=min(168,max(70,h-330))
        panel_height=photo_height+146
        x,y=max(12,w-width-18),70
        panel=pygame.Surface((width,panel_height),pygame.SRCALPHA)
        pygame.draw.rect(panel,(0,0,0,145),panel.get_rect(),border_radius=12)
        self.screen.blit(panel,(x,y))
        self.text(f'SEAL {index+1}/{len(target)}  /  {sign.upper()}',x+14,y+12,(225,247,255),self.small)
        image=self.guide_images.get(sign)
        if image is not None:
            key=(sign,width,photo_height)
            if key not in self.guide_scaled:
                ratio=min((width-28)/image.get_width(),photo_height/image.get_height())
                self.guide_scaled[key]=pygame.transform.smoothscale(image,(max(1,int(image.get_width()*ratio)),max(1,int(image.get_height()*ratio))))
            photo=self.guide_scaled[key]
            self.screen.blit(photo,(x+(width-photo.get_width())//2,y+42))
        if demo:
            key={'ox':'1','hare':'2','monkey':'3'}.get(sign,'?')
            lines=(f'Press {key} to confirm this seal','Camera preview + key input')
        elif needs_neutral:
            lines=('Clear hands from the frame.','Then make '+sign.upper()+'.')
        else:
            lines=('Match the hand pose above.','Hold steady to confirm.')
        for i,line in enumerate(lines):
            self.text(line,x+14,y+photo_height+56+i*27,(235,244,250),self.small)

    def cinematic(self,elapsed,jutsu):
        w,h=self.screen.get_size()
        if self.animation is not None:
            index=self.animation.frame_index(elapsed)
            frame=self.animation.frames[index]
            # Fit the whole anime shot; a dimmed cover copy fills side margins.
            key=(index,w,h)
            if key not in self.animation_scaled:
                if len(self.animation_scaled)>len(self.animation.frames)*2:
                    self.animation_scaled.clear()
                fw,fh=frame.get_size()
                cover=max(w/fw,h/fh);fit=min(w/fw,h/fh)
                background=pygame.transform.smoothscale(frame,(max(w,round(fw*cover)),max(h,round(fh*cover))))
                foreground=pygame.transform.smoothscale(frame,(max(1,round(fw*fit)),max(1,round(fh*fit))))
                self.animation_scaled[key]=(background,foreground)
            background,foreground=self.animation_scaled[key]
            self.screen.blit(background,background.get_rect(center=(w//2,h//2)))
            shade=pygame.Surface((w,h),pygame.SRCALPHA);shade.fill((0,0,0,155))
            self.screen.blit(shade,(0,0))
            self.screen.blit(foreground,foreground.get_rect(center=(w//2,h//2)))
            title=self.font.render('CHIDORI!',True,(225,250,255))
            shadow=self.font.render('CHIDORI!',True,(0,0,0))
            self.screen.blit(shadow,(26,h-54));self.screen.blit(title,(24,h-56))
            return
        self.screen.fill((5,9,28))
        # Accelerating speed lines pull the eye toward the charged hand.
        charge=min(1.0,max(0.0,elapsed/1.1))
        for i in range(36):
            angle=i*math.tau/36
            travel=(elapsed*480+i*43)%max(w,h)
            radius=100+travel
            origin=(w*.67,h*.44)
            points=[(int(origin[0]+math.cos(angle)*r),int(origin[1]+math.sin(angle)*r)) for r in (radius,radius+60+charge*75)]
            pygame.draw.line(self.screen,(15,35,66),points[0],points[1],2)
        for k in range(5):
            r=60+int((elapsed*90+k*85)%420);pygame.draw.circle(self.screen,(9,30+k*2,70+k*4),(int(w*.55),int(h*.49)),r,2)
        if self.art:
            maxw,maxh=int(w*.67),int(h*.82);ratio=min(maxw/self.art.get_width(),maxh/self.art.get_height())*(.86+.14*charge+.018*math.sin(elapsed*5))
            size=(max(1,int(self.art.get_width()*ratio)),max(1,int(self.art.get_height()*ratio)))
            if self.scaled_key != size:
                self.scaled_art=pygame.transform.smoothscale(self.art,size);self.scaled_key=size
            img=self.scaled_art
            art_rect=img.get_rect(center=(int(w*(.70-.05*charge)),int(h*.49+4*math.sin(elapsed*4))))
            self.screen.blit(img,art_rect)
            effect_center=(art_rect.x+int(img.get_width()*.73),art_rect.y+int(img.get_height()*.36))
        else:
            # Deliberately generic silhouette, not copyrighted character art.
            cx=int(w*.65);cy=int(h*.50)
            effect_center=(cx+90,cy)
            pygame.draw.circle(self.screen,(19,35,70),(cx,cy-145),58)
            pygame.draw.polygon(self.screen,(21,41,83),[(cx-78,cy-80),(cx+70,cy-80),(cx+110,cy+220),(cx-112,cy+220)])
            pygame.draw.line(self.screen,(25,50,104),(cx+35,cy-60),(cx+130,cy+20),30)
            self.text('IMAGE UNAVAILABLE - CHECK CONFIG / LOG',28,h-87,(100,150,204),self.small)
            self.text(str(jutsu.get('image', 'No image configured')),28,h-60,(100,150,204),self.small)
        self.lightning.draw(self.screen,elapsed,effect_center)
        title=self.big.render('CHIDORI!' if elapsed>.65 else 'CHARGING...',True,(164,234,255))
        title.set_alpha(min(255,int(elapsed*500)))
        self.screen.blit(title,(45+int(22*math.exp(-elapsed*4)),h-210))
        self.text('LIGHTNING STYLE  //  '+jutsu['character'].upper(),50,h-108,(135,182,241),self.small)
