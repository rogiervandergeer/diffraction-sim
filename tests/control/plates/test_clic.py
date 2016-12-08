from control.plates.clic import ClicPlate
from math import pi
from numpy import mean


def test_gap():
    cp = ClicPlate(diameter=0.1, dimension=10, tool_size=0,
                   inner_diameter=0.05, outer_diameter=0.09)
    assert abs(cp.gap - 0.02) < 1e-9


def test_strut_angle_rotation():
    for rotation in [0, 0.1, 0.2]:
        cp = ClicPlate(diameter=0.1, dimension=10, tool_size=0,
                       inner_diameter=0.05, outer_diameter=0.09,
                       n_struts=4, rotation=rotation)
        assert cp.strut_angles[0] == rotation
        assert abs(cp.strut_angles[-1] - (2*pi) - rotation) < 1e-9
        assert abs(mean(cp.strut_angles) - pi - rotation) < 1e-9


def test_strut_angle_mod_rotation():
    for n_struts in range(1, 10):
        cp = ClicPlate(diameter=0.1, dimension=10, tool_size=0,
                       inner_diameter=0.05, outer_diameter=0.09,
                       n_struts=n_struts, rotation=1)
        assert cp.strut_angles[0] == 1 % (2*pi/n_struts)


def test_strut_angles():
    for n_struts in range(1, 16):
        cp = ClicPlate(diameter=0.1, dimension=10, tool_size=0,
                       inner_diameter=0.05, outer_diameter=0.09,
                       n_struts=n_struts)
        assert len(cp.strut_angles) == n_struts + 1
        assert len(set(cp.strut_angles)) == n_struts + 1
        assert cp.strut_angles[0] == 0
        assert abs(cp.strut_angles[-1] - (2*pi)) < 1e-9
        assert abs(mean(cp.strut_angles) - pi) < 1e-9