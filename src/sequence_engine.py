"""Model-independent, longest-prefix jutsu matcher."""
from dataclasses import dataclass

@dataclass
class SequenceEvent:
    status: str
    signs: tuple
    jutsu: dict | None = None

class SequenceEngine:
    def __init__(self, jutsus, timeout=12.0):
        self.jutsus = jutsus
        self.timeout = timeout
        self.signs = []
        self.last_at = None

    def reset(self):
        self.signs.clear()
        self.last_at = None

    def expire(self, now):
        if self.last_at is not None and now-self.last_at > self.timeout:
            self.reset()
            return True
        return False

    def accept(self, sign, now):
        self.expire(now)
        sign = sign.lower()
        trial = self.signs + [sign]
        possible = [j for j in self.jutsus if j['signs'][:len(trial)] == trial]
        if not possible:
            # Recover gracefully: restart at longest suffix that is a valid prefix.
            for start in range(1,len(trial)):
                suffix=trial[start:]
                if any(j['signs'][:len(suffix)] == suffix for j in self.jutsus):
                    trial=suffix
                    break
            else:
                trial=[]
            self.signs=trial
            self.last_at=now if trial else None
            return SequenceEvent('recovered' if trial else 'incorrect',tuple(trial))
        self.signs=trial
        self.last_at=now
        exact=[j for j in possible if len(j['signs']) == len(trial)]
        longer=[j for j in possible if len(j['signs']) > len(trial)]
        if exact and not longer:
            match=exact[0]
            completed=tuple(trial)
            self.reset()
            return SequenceEvent('activated',completed,match)
        return SequenceEvent('progress',tuple(trial))
