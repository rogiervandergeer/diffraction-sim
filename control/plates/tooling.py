from math import ceil, floor
from numpy import array


def tooled(plate, tool_diameter):
    """Create a copy of plate that can be created with a circular tool.

    When a physical plate is to be created with a circular tool, i.e. a drill,
    it cannot contain straight angles. This function creates a plate similar
    to the provided plate that can be created with such a tool.

    This is achieved by checking for each grid-location on the plate whether
    all grid-points in the circle of the tool size around that point are
    transparent. If so, then those points are made transparent on the resulting
    plate.

    In the case of gradients, the tooling procedure is applied for each
    transparency level in order from opaque to transparent.

    Args:
        plate (2d array): Plate on which the result will be based.
        tool_diameter (float): Diameter of the tool to be used,
            in units of one grid-spacing.

    Returns:
        np.array, tooled copy of the input plate.
    """
    if tool_diameter < 2:
        return plate.copy()
    retval = array([[0] * plate.shape[1]] * plate.shape[0])
    for value in nonzero_unique(plate):
        for x in range(plate.shape[0]):
            for y in range(plate.shape[1]):
                if check_circle(plate, (x, y), tool_diameter*0.5, value):
                    fill_circle(retval, (x, y), tool_diameter*0.5, value)
    return retval


def check_circle(plate, offset, radius, value):
    """Check if all values in a circle on the plate are at least a given value.

    Args:
        plate (2d array): Plate to check the entries of.
        offset (tuple [int, int]): Center coordinates of the circle.
        radius (float): Radius of the circle.
        value (int): Value to compare to.

    Returns:
        bool, True if all entries inside the circle are >= value
    """
    for x, y in circle_coordinates(plate.shape, offset, radius):
        if plate[x][y] < value:
            return False
    return True


def fill_circle(plate, offset, radius, value):
    """Fill a circle of size around offset in the plate with a value.

    Args:
        plate (2d array): Array to fill the entries in.
        offset (tuple [int, int]): Center coordinates of the circle.
        radius (float): Radius of the circle.
        value (int): Value to fill all entries in the circle with.
    """
    for x, y in circle_coordinates(plate.shape, offset, radius):
        plate[x][y] = value


def circle_coordinates(shape, offset, size):
    """Generate (x, y) coordinates in a circle of a given size.

    Args:
        shape (tuple): Shape of the array we are working on.
        offset (tuple [int, int]): Center coordinate of the circle.
        size (float): Size of the circle.

    Yields:
        tuple [int]: (x, y)-coordinate
    """
    ssq = size**2
    x, y = offset
    for dx in range(max(ceil(-size), -x), min(floor(size+1), shape[0]-x)):
        for dy in range(max(ceil(-size), -y), min(floor(size+1), shape[1]-y)):
            if dx**2 + dy**2 <= ssq:
                yield (x+dx, y+dy)


def nonzero_unique(plate):
    """Find all nonzero unique values in a 2d array.

    Args:
        plate (2d iterable): Array to find the unique values of.

    Returns:
        set: of all nonzero values
    """
    return set(value for row in plate for value in row if value > 0)
