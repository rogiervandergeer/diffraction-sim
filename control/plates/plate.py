from abc import abstractmethod
from math import sqrt

import numpy as np
from matplotlib.pyplot import imshow, figure

from control.plates.tooling import tooled


class Plate:

    def __init__(self, diameter, dimension, tool_size=None):
        self.diameter = diameter
        self.dimension = dimension
        self.tool_size = tool_size
        self.check()

    def __repr__(self):
        return '{cls}({vars})'.format(
            cls=self.__class__.__name__,
            vars=', '.join(sorted('{k}={v}'.format(k=k, v=repr(v))
                                  for k, v in self.__dict__.items()))
        )

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
        if 'type' not in definition:
            raise ValueError('Cannot create plate: no type specified.')
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
        """Build the plate.

        Returns:
            numpy.array
        """
        raw = np.array([
            [self.calc(row, col) for col in range(self.dimension)]
            for row in range(self.dimension)
        ], dtype=np.uint8)
        if not self.tool_size:
            return raw
        return tooled(raw, self.tool_size/self.delta)

    def calc(self, row, col):
        """Calculate the opacity of a point.

        Args:
            row (int): Row index of the point.
            col (int): Column index of the point.

        Returns:
            float
        """
        return self.opacity(x=self.position(col), y=self.position(row))

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def opacity(self, x, y):
        return 0

    @property
    def delta(self):
        """Compute the distance between points on the plate.

        Returns:
            float
        """
        return self.diameter / self.dimension

    def position(self, index):
        """Compute the position along either of the axes at a given point.

        Args:
            index (int): Index along the axis of the given point.

        Returns:
            float
        """
        return self.delta * (index - (0.5*(self.dimension - 1)))

    def show(self, fig_size=(10, 10)):
        """Compute an image of the plate.

        Args:
            fig_size (tuple[float]): Size of the figure. Defaults to (10, 10).

        Returns:
            pyplot.figure
        """
        fig = figure(figsize=fig_size)
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
