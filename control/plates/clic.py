from math import atan2, cos, pi, sin, sqrt
from control.plates import Plate


class ClicPlate(Plate):

    def __init__(self,
                 diameter,
                 dimension,
                 inner_diameter,
                 outer_diameter,
                 n_struts,
                 strut_width,
                 rotation=0.0):
        self.inner_diameter = inner_diameter
        self.outer_diameter = outer_diameter
        self.n_struts = n_struts
        self.strut_width = strut_width
        self.rotation = rotation
        super().__init__(diameter, dimension)

    def check(self):
        pass

    def opacity(self, x, y):
        d = 2*sqrt(x*x + y*y)
        if d < self.inner_diameter or d > self.outer_diameter:
            return 0
        if self.n_struts == 0:
            return 255
        ang = atan2(y, x) % (2*pi)
        retval = 255
        for strut_ang in self.strut_angles:
            d_ang = abs(strut_ang - ang)
            if d_ang <= 0.5 * self.strut_width:
                return 0
        return retval

    @property
    def strut_angles(self):
        if self.n_struts == 0:
            return []
        return [
            self.rotation + (2*pi*idx)/self.n_struts
            for idx in range(self.n_struts+1)
        ]