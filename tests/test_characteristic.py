import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from math import isclose, pi

from common.r3 import R3
from shadow.polyedr import Edge, Facet, Polyedr, Segment


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

    def test_visibility_classes_and_reset_gaps(self):
        e = Edge(R3(0.0, 0.0, 0.0), R3(1.0, 0.0, 0.0))

        self.assertTrue(e.is_fully_visible())
        self.assertFalse(e.is_partly_visible())
        self.assertFalse(e.is_fully_invisible())

        e.gaps = [Segment(0.0, 0.5)]
        self.assertFalse(e.is_fully_visible())
        self.assertTrue(e.is_partly_visible())
        self.assertFalse(e.is_fully_invisible())

        e.gaps = []
        self.assertFalse(e.is_fully_visible())
        self.assertFalse(e.is_partly_visible())
        self.assertTrue(e.is_fully_invisible())

        e.reset_gaps()
        self.assertTrue(e.is_fully_visible())

    def test_vertical_normal_can_be_reversed(self):
        f = Facet([
            R3(0.0, 0.0, 0.0),
            R3(0.0, 2.0, 0.0),
            R3(2.0, 2.0, 0.0),
            R3(2.0, 0.0, 0.0),
        ])

        self.assertLess(f.v_normals()[0].y, 0.0)


class TestCharacteristicIntegration(unittest.TestCase):

    def _write_geom(self, content):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".geom", delete=False)
        tmp.write(content)
        tmp.close()
        return tmp.name

    def test_print_hidden_edge_projection_sum(self):
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
        stream = StringIO()

        with redirect_stdout(stream):
            p.print_hidden_edge_projection_sum()

        self.assertIn("4.0", stream.getvalue())

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

    def test_scale_angles_do_not_change_value(self):
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
