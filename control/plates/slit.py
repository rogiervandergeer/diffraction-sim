from control.plates import Plate


class SlitPlate(Plate):

    def __init__(self, diameter, dimension, n_slits, width, height, distance):
        self.n_slits = n_slits
        self.width = width
        self.height = height
        self.distance = distance
        super().__init__(diameter, dimension)

    def check(self):
        if self.n_slits < 1:
            raise ValueError('must have at least one slit')
        if self.width < 0 or self.height < 0:
            raise ValueError('all dimensions must be positive')
        if self.distance < self.width:
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
