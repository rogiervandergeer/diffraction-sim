from math import sqrt

from control.plates import Plate


class BandPlate(Plate):
    """Describes a plate with a single circular band.

    Args:
        diameter (float): Physical diameter of the plate.
        dimension (int): Number of points along each of the axes of the plate.
        outer_diameter (float): The outer diameter of the band. Must be > 0.
        inner_diameter (float): The inner diameter of the band. If equal to 0,
            the plate will be a circle. Defaults to 0.
        tool_size (float/None): Tool size used to construct the plate. Any concave
            edges with a diameter smaller than the tool size will be rounded such
            that they can be created with a circular tool (i.e. drill). If None,
            do not apply tooling. Defaults to None.
    """

    def __init__(self,
                 diameter,
                 dimension,
                 outer_diameter,
                 inner_diameter=0,
                 tool_size=None):
        self.inner_diameter = inner_diameter
        self.outer_diameter = outer_diameter
        super().__init__(diameter=diameter, dimension=dimension, tool_size=tool_size)

    def check(self):
        if self.outer_diameter > self.diameter:
            raise ValueError('outer diameter of plate too large')
        if self.outer_diameter <= self.inner_diameter:
            raise ValueError('outer diameter must be > inner diameter')
        if self.inner_diameter < 0:
            raise ValueError('inner diameter cannot be < 0')

    def opacity(self, x, y):
        d = 2 * sqrt(x*x + y*y)
        if d < self.inner_diameter or d > self.outer_diameter:
            return 0
        return 255

    @property
    def gap(self):
        """Compute the width of the band. the distance between the inner and outer edges."""
        return 0.5 * (self.outer_diameter - self.inner_diameter)
