from dataclasses import dataclass
@dataclass
class Coordinate:
    ra: float
    dec: float

    def __init__(self, ra, dec):
        self._ra = ra
        self._dec = dec

    @property
    def ra(self):
        return self._ra

    @ra.setter
    def ra(self, new_ra):
        self._ra = new_ra

    @property
    def dec(self):
        return self._dec

    @dec.setter
    def dec(self, new_dec):
        self._dec = new_dec