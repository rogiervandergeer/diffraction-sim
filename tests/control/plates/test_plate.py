from control.plates.plate import Plate, CirclePlate


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


def test_create():
    p = Plate.create({'dimension': 10, 'diameter': 1,
                      'type': 'CirclePlate', 'circle_diameter': 1})
    assert isinstance(p, CirclePlate)
    assert p.dimension == 10
    assert p.diameter == 1
    assert p.circle_diameter == 1


def test_circle_opacity():
    p = CirclePlate(1, 11, 1)
    b = p.build()
    assert b.shape == (11, 11)
    assert b[0][0] == 0
    assert b[5][5] == 255
    for i in range(11):
        for j in range(11):
            assert b[i][j] == b[10-i][j]
            assert b[i][j] == b[i][10-j]
    assert b[0][3] == 255
    assert b[0][2] == 0
