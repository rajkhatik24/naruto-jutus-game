class TemporalFilter:
    """Require stable consecutive frames, then neutral frames to arm next sign."""
    def __init__(self,stable_frames=5,neutral_frames=4):
        self.stable_frames=stable_frames
        self.neutral_frames=neutral_frames
        self.label=None;self.count=0;self.neutral_count=0;self.armed=True
    def reset(self):
        self.label=None;self.count=0;self.neutral_count=0;self.armed=True
    def feed(self,label):
        if label is None:
            self.label=None;self.count=0;self.neutral_count+=1
            if self.neutral_count>=self.neutral_frames:self.armed=True
            return None
        self.neutral_count=0
        if label!=self.label:self.label=label;self.count=1
        else:self.count+=1
        if self.armed and self.count>=self.stable_frames:
            self.armed=False
            return label
        return None
