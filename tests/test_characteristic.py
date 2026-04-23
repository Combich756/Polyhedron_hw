import unittest
import tempfile
from math import pi, isclose
from shadow.polyedr import Edge, Polyedr
from common.r3 import R3


class TestCharacteristicHelpers(unittest.TestCase):

    def test_projection_length(self):
        e = Edge(R3(0.0, 0.0, 0.0), R3(3.0, 4.0, 10.0))
        self.assertTrue(isclose(e.projection_length(), 5.0))

    def test_angle_filter_accepts_small_angle(self):
        e = Edge(R3(0.0, 0.0, 0.0), R3(10.0, 0.0, 1.0))
        self.assertLessEqual(e.angle_with_horizontal(), pi / 7.0)

    def test_angle_filter_rejects_large_angle(self):
        e = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 0.0, 2.0))
        self.assertGreater(e.angle_with_horizontal(), pi / 7.0)

    def test_center_projection_distance_to_x2(self):
        e = Edge(R3(1.0, 0.0, 0.0), R3(2.4, 1.0, 0.0))
        self.assertTrue(isclose(e.projected_center_distance_to_x2(), 0.3))


class TestCharacteristicIntegration(unittest.TestCase):

    def _write_geom(self, content):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".geom", delete=False)
        tmp.write(content)
        tmp.close()
        return tmp.name

    def test_hidden_lower_square_gives_sum_4(self):
        # Верхняя горизонтальная грань полностью закрывает нижнюю
        # квадратную грань. У всех четырёх нижних рёбер угол 0,
        # а проекция центра находится на расстоянии < 1 от прямой x=2.
        path = self._write_geom(
            """1 0 0 0
8 2 8
0.5 0.0 1.0
2.5 0.0 1.0
2.5 2.0 1.0
0.5 2.0 1.0
1.2 0.5 0.0
2.2 0.5 0.0
2.2 1.5 0.0
1.2 1.5 0.0
4 1 2 3 4
4 5 6 7 8
"""
        )
        p = Polyedr(path)
        self.assertTrue(isclose(p.hidden_edge_projection_sum(), 4.0))

    def test_same_polyhedron_with_other_scale_and_angles_gives_same_value(self):
        geom1 = """1 0 0 0
8 2 8
0.5 0.0 1.0
2.5 0.0 1.0
2.5 2.0 1.0
0.5 2.0 1.0
1.2 0.5 0.0
2.2 0.5 0.0
2.2 1.5 0.0
1.2 1.5 0.0
4 1 2 3 4
4 5 6 7 8
"""
        geom2 = """7 35 -20 15
8 2 8
0.5 0.0 1.0
2.5 0.0 1.0
2.5 2.0 1.0
0.5 2.0 1.0
1.2 0.5 0.0
2.2 0.5 0.0
2.2 1.5 0.0
1.2 1.5 0.0
4 1 2 3 4
4 5 6 7 8
"""
        p1 = Polyedr(self._write_geom(geom1))
        p2 = Polyedr(self._write_geom(geom2))
        self.assertTrue(isclose(p1.hidden_edge_projection_sum(), 4.0))
        self.assertTrue(isclose(p2.hidden_edge_projection_sum(), 4.0))

    def test_strict_inequality_for_distance_to_x2(self):
        # Нижняя грань скрыта полностью, но центры двух вертикальных рёбер
        # лежат на расстоянии ровно 1 от прямой x=2, поэтому не учитываются.
        # Считаются только верхнее и нижнее рёбра длины 2.
        path = self._write_geom(
            """1 0 0 0
8 2 8
0.0 0.0 1.0
4.0 0.0 1.0
4.0 2.0 1.0
0.0 2.0 1.0
1.0 0.5 0.0
3.0 0.5 0.0
3.0 1.5 0.0
1.0 1.5 0.0
4 1 2 3 4
4 5 6 7 8
"""
        )
        p = Polyedr(path)
        self.assertTrue(isclose(p.hidden_edge_projection_sum(), 4.0))
