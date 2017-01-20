from math import atan2, pi

from control.plates.band import BandPlate


class ClicPlate(BandPlate):
    """Describes a plate with a single circular band connected with struts.

    This plate is similar to the BandPlate, except that the inner circle is
    connected to the outer rim by a number of struts at regular intervals.

    Args:
        diameter (float): Physical diameter of the plate.
        dimension (int): Number of points along each of the axes of the plate.
        outer_diameter (float): The outer diameter of the band. Must be > 0.
        inner_diameter (float): The inner diameter of the band. If equal to 0,
            the plate will be a circle. Defaults to 0.
        n_struts (int): The number of struts. Defaults to 0.
        tool_size (float/None): Tool size used to construct the plate. Any concave
            edges with a diameter smaller than the tool size will be rounded such
            that they can be created with a circular tool (i.e. drill). If None,
            do not apply tooling. Defaults to None.
        strut_width (float): The width of the struts in radians. Defaults to 0.1.
        rotation (float): Angle in radians of the position of the first strut.
            Defaults to 0.
    """

    def __init__(self,
                 diameter,
                 dimension,
                 outer_diameter,
                 inner_diameter=0,
                 n_struts=0,
                 tool_size=0,
                 strut_width=0.1,
                 rotation=0.0):
        self.n_struts = n_struts
        self.strut_width = strut_width
        self.rotation = rotation % (2*pi/(n_struts if n_struts else 1))
        super().__init__(diameter=diameter, dimension=dimension, tool_size=tool_size,
                         inner_diameter=inner_diameter, outer_diameter=outer_diameter)

    def check(self):
        BandPlate.check(self)
        if self.n_struts < 0:
            raise ValueError('cannot have negative struts')
        if self.strut_width * self.n_struts >= 2*pi:
            raise ValueError('too many or too large struts')
        if self.tool_size + self.delta > self.gap:
            raise ValueError('Tool size too large.')

    def opacity(self, x, y):
        if BandPlate.opacity(self, x, y) == 0:
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
        """Generate the polar angles at which the struts are located.

        Unless the number of struts equals 0, n+1 struts are generated
        such that in the case that the first strut is positioned across
        angle == 0 the last strut will complete that strut on the other
        side of the border.

        Yields:
            float
        """
        if self.n_struts > 0:
            for idx in range(self.n_struts+1):
                yield self.rotation + (2*pi*idx)/self.n_struts
