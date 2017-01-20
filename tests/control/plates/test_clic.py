from math import pi
from unittest import TestCase

from numpy import mean

from control.plates.clic import ClicPlate


class ClicTest(TestCase):

    def test_x(self):
        pass


def test_gap():
    cp = ClicPlate(diameter=0.1, dimension=10, tool_size=0,
                   inner_diameter=0.05, outer_diameter=0.09)
    assert abs(cp.gap - 0.02) < 1e-9


def test_strut_angle_rotation():
    for rotation in [0, 0.1, 0.2]:
        cp = ClicPlate(diameter=0.1, dimension=10, tool_size=0,
                       inner_diameter=0.05, outer_diameter=0.09,
                       n_struts=4, rotation=rotation)
        angles = list(cp.strut_angles)
        assert angles[0] == rotation
        assert abs(angles[-1] - (2*pi) - rotation) < 1e-9
        assert abs(mean(angles) - pi - rotation) < 1e-9


def test_strut_angle_mod_rotation():
    for n_struts in range(1, 10):
        cp = ClicPlate(diameter=0.1, dimension=10, tool_size=0,
                       inner_diameter=0.05, outer_diameter=0.09,
                       n_struts=n_struts, rotation=1)
        angles = list(cp.strut_angles)
        assert angles[0] == 1 % (2*pi/n_struts)


def test_strut_angles():
    for n_struts in range(1, 16):
        cp = ClicPlate(diameter=0.1, dimension=10, tool_size=0,
                       inner_diameter=0.05, outer_diameter=0.09,
                       n_struts=n_struts)
        angles = list(cp.strut_angles)
        assert len(angles) == n_struts + 1
        assert len(set(angles)) == n_struts + 1
        assert angles[0] == 0
        assert abs(angles[-1] - (2*pi)) < 1e-9
        assert abs(mean(angles) - pi) < 1e-9
