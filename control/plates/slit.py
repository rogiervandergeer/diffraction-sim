from control.plates import Plate


class SlitPlate(Plate):
    """Describes a plate with a number of parallel rectangular slits.

    Args:
        diameter (float): Physical diameter of the plate.
        dimension (int): Number of points along each of the axes of the plate.
        n_slits (int): Number of slits. Must be at least 1.
        width (float): Width of the slits.
        height (float): Height of the slits.
        tool_size (float/None): Tool size used to construct the plate. Any concave
            edges with a diameter smaller than the tool size will be rounded such
            that they can be created with a circular tool (i.e. drill). If None,
            do not apply tooling. Defaults to None.
        distance (float): Distance between the centers of the slits. If N_slits > 1
            this must be larger than the width of the slits. Defaults to 0.
    """

    def __init__(self, diameter, dimension,
                 n_slits, width, height,
                 tool_size=None, distance=0.):
        self.n_slits = n_slits
        self.width = width
        self.height = height
        self.distance = distance
        super().__init__(diameter, dimension, tool_size)

    def check(self):
        if self.n_slits < 1:
            raise ValueError('must have at least one slit')
        if self.width < 0 or self.height < 0:
            raise ValueError('all dimensions must be positive')
        if self.distance < self.width and self.n_slits > 1:
            raise ValueError('slits overlap')
        if self.n_slits * self.distance + self.width > self.diameter:
            raise ValueError('slits do not fit')

    def opacity(self, x, y):
        if abs(2*y) > self.height:
            return 0
        for location in ((i - (0.5 * (self.n_slits - 1))) * self.distance
                         for i in range(self.n_slits)):
            if x < location - self.width * 0.5:
                continue
            if x > location + self.width * 0.5:
                continue
            return 255
        return 0
