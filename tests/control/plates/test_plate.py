from control.plates.plate import Plate


def test_build():
    p = Plate(1, 10)
    b = p.build()
    assert b.shape == (10, 10)


def test_delta():
    p = Plate(1, 2)
    assert p.delta == 0.5


def test_position():
    p = Plate(1, 2)
    assert p.position(0) == -0.25
    assert p.position(1) == 0.25
