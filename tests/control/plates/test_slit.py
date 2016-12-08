from control.plates.slit import SlitPlate


def test_split():
    sp = SlitPlate(diameter=.5, dimension=5, tool_size=0,
                   n_slits=2, width=0.1, height=0.3, distance=0.2)
    q = sp.build()
    assert (q == [[0, 0, 0, 0, 0],
                  [0, 255, 0, 255, 0],
                  [0, 255, 0, 255, 0],
                  [0, 255, 0, 255, 0],
                  [0, 0, 0, 0, 0]]).all()

    sp = SlitPlate(diameter=0.5, dimension=5, tool_size=0,
                   n_slits=1, width=0.3, height=0.3, distance=0.2)
    q = sp.build()
    assert (q == [[0, 0, 0, 0, 0],
                  [0, 255, 255, 255, 0],
                  [0, 255, 255, 255, 0],
                  [0, 255, 255, 255, 0],
                  [0, 0, 0, 0, 0]]).all()

