import numpy as np
from math import sqrt
from matplotlib.pyplot import imshow, figure
from control.plates.tooling import tooled


class Plate:

    def __init__(self, diameter, dimension, tool_size=None):
        self.diameter = diameter
        self.dimension = dimension
        self.tool_size = tool_size
        self.check()

    @classmethod
    def create(cls, definition):
        """
        Create a plate according to a definition.

        Args:
            definition (dict): Dictionary containing a key 'type' of which the
                value matches the name of one of the plate subclasses, and keys
                for all arguments required by that plate.

        Returns:
            Plate: an instance of one of the sub-types of Plate
        """
        sub_cls = cls.select(definition['type'])
        return sub_cls(
            **{key: val for key, val in definition.items()  if key != 'type'}
        )

    @classmethod
    def select(cls, name):
        for sub_cls in cls.__subclasses__():
            if name == sub_cls.__name__:
                return sub_cls
        raise ValueError('No such plate class:', name)

    def build(self):
        raw = np.array([
            [self.calc(row, col) for col in range(self.dimension)]
            for row in range(self.dimension)
        ], dtype=np.uint8)
        if not self.tool_size:
            return raw
        return tooled(raw, self.tool_size/self.delta)

    def calc(self, row, col):
        return self.opacity(x=self.position(col), y=self.position(row))

    def check(self):
        pass

    def opacity(self, x, y):
        return 0

    @property
    def delta(self):
        return self.diameter / self.dimension

    def position(self, index):
        return self.delta * (index - (0.5*(self.dimension - 1)))

    def show(self, figsize=(10, 10)):
        fig = figure(figsize=figsize)
        ax = imshow(self.build(), cmap='gray')
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        return fig


class CirclePlate(Plate):

    def __init__(self, diameter, dimension, circle_diameter):
        self.circle_diameter = circle_diameter
        super().__init__(diameter, dimension)

    def check(self):
        if self.circle_diameter > self.diameter:
            raise ValueError('circle diameter of plate too large')

    def opacity(self, x, y):
        radius = sqrt(x*x + y*y)
        if 2*radius <= self.circle_diameter:
            return 255
        return 0
