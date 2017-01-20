from control.plates.band import BandPlate
from unittest import TestCase
from math import pi


class BandTest(TestCase):

    def test_small(self):
        sp = BandPlate(diameter=.5, dimension=5, outer_diameter=.5)
        q = sp.build()
        self.assertTrue((q == [[0, 255, 255, 255, 0],
                               [255, 255, 255, 255, 255],
                               [255, 255, 255, 255, 255],
                               [255, 255, 255, 255, 255],
                               [0, 255, 255, 255, 0]]).all())

        sp = BandPlate(diameter=.5, dimension=5, outer_diameter=.5, inner_diameter=0.3)
        q = sp.build()
        self.assertTrue((q == [[0, 255, 255, 255, 0],
                               [255, 0, 0, 0, 255],
                               [255, 0, 0, 0, 255],
                               [255, 0, 0, 0, 255],
                               [0, 255, 255, 255, 0]]).all())

    def test_surface(self):
        p = BandPlate(diameter=.5, dimension=1000, outer_diameter=.5).build()
        surface = p.sum()*1E-6/255
        self.assertAlmostEqual(surface, pi*0.25, places=3)

        p = BandPlate(diameter=.5, dimension=1000,
                      outer_diameter=.5, inner_diameter=0.4).build()
        surface = p.sum() * 1E-6 / 255
        self.assertAlmostEqual(surface, pi * (0.25-0.16), places=3)

    def test_gap(self):
        cp = BandPlate(diameter=0.1, dimension=10, tool_size=0,
                       inner_diameter=0.05, outer_diameter=0.09)
        self.assertAlmostEqual(cp.gap, 0.02)
