from math import atan2, pi
from functools import reduce
from operator import add
from common.r3 import R3


class Segment:
    """ Одномерный отрезок """

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin

    def is_degenerate(self):
        return self.beg >= self.fin

    def intersect(self, other):
        if other.beg > self.beg:
            self.beg = other.beg
        if other.fin < self.fin:
            self.fin = other.fin
        return self

    def subtraction(self, other):
        return [
            Segment(
                self.beg,
                self.fin if self.fin < other.beg else other.beg,
            ),
            Segment(
                self.beg if self.beg > other.fin else other.fin,
                self.fin,
            ),
        ]


class Edge:
    """ Ребро полиэдра """

    SBEG, SFIN = 0.0, 1.0

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]

    def clone(self):
        return Edge(self.beg, self.fin)

    def reset_gaps(self):
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]

    def shadow(self, facet):
        if facet.is_vertical():
            return

        shade = Segment(Edge.SBEG, Edge.SFIN)
        for u, v in zip(facet.vertexes, facet.v_normals()):
            shade.intersect(self.intersect_edge_with_normal(u, v))
            if shade.is_degenerate():
                return

        shade.intersect(
            self.intersect_edge_with_normal(
                facet.vertexes[0], facet.h_normal(),
            ),
        )
        if shade.is_degenerate():
            return

        gaps = [s.subtraction(shade) for s in self.gaps]
        self.gaps = [
            s for s in reduce(add, gaps, []) if not s.is_degenerate()
        ]

    def r3(self, t):
        return self.beg * (Edge.SFIN - t) + self.fin * t

    def intersect_edge_with_normal(self, a, n):
        f0, f1 = n.dot(self.beg - a), n.dot(self.fin - a)
        if f0 >= 0.0 and f1 >= 0.0:
            return Segment(Edge.SFIN, Edge.SBEG)
        if f0 < 0.0 and f1 < 0.0:
            return Segment(Edge.SBEG, Edge.SFIN)
        x = -f0 / (f1 - f0)
        return Segment(Edge.SBEG, x) if f0 < 0.0 else Segment(x, Edge.SFIN)

    def is_fully_invisible(self):
        return len(self.gaps) == 0

    def is_fully_visible(self):
        return (
            len(self.gaps) == 1
            and self.gaps[0].beg == Edge.SBEG
            and self.gaps[0].fin == Edge.SFIN
        )

    def is_partly_visible(self):
        return not self.is_fully_visible() and not self.is_fully_invisible()

    def vector(self):
        return self.fin - self.beg

    def projection_length(self):
        v = self.vector()
        return (v.x * v.x + v.y * v.y) ** 0.5

    def angle_with_horizontal(self):
        v = self.vector()
        return atan2(abs(v.z), self.projection_length())

    def center(self):
        return self.r3(0.5)

    def projected_center_distance_to_x2(self):
        return abs(self.center().x - 2.0)


class Facet:
    """ Грань полиэдра """

    def __init__(self, vertexes):
        self.vertexes = vertexes

    def is_vertical(self):
        return self.h_normal().dot(Polyedr.V) == 0.0

    def h_normal(self):
        n = (
            self.vertexes[1] - self.vertexes[0]
        ).cross(self.vertexes[2] - self.vertexes[0])
        return n * (-1.0) if n.dot(Polyedr.V) < 0.0 else n

    def v_normals(self):
        return [self._vert(x) for x in range(len(self.vertexes))]

    def _vert(self, k):
        n = (self.vertexes[k] - self.vertexes[k - 1]).cross(Polyedr.V)
        if n.dot(self.vertexes[k - 1] - self.center()) < 0.0:
            return n * (-1.0)
        return n

    def center(self):
        return sum(
            self.vertexes,
            R3(0.0, 0.0, 0.0),
        ) * (1.0 / len(self.vertexes))


class Polyedr:
    """ Полиэдр """

    V = R3(0.0, 0.0, 1.0)
    MAX_ANGLE = pi / 7.0
    CENTER_LINE_X = 2.0
    MAX_CENTER_DISTANCE = 1.0

    def __init__(self, filename):
        self.vertexes, self.edges, self.facets = [], [], []
        self.base_vertexes, self.base_facets = [], []
        self.unique_base_edges = []

        unique_edges = {}

        with open(filename, encoding="utf-8") as geom_file:
            lines = [line for line in geom_file if line.split()]

        for i, line in enumerate(lines):
            if i == 0:
                buf = line.split()
                c = float(buf.pop(0))
                alpha, beta, gamma = (
                    float(x) * pi / 180.0 for x in buf
                )
            elif i == 1:
                nv = int(line.split()[0])
            elif i < nv + 2:
                x, y, z = (float(x) for x in line.split())
                base = R3(x, y, z)
                self.base_vertexes.append(base)
                self.vertexes.append(base.rz(alpha).ry(beta).rz(gamma) * c)
            else:
                self._add_facet(line, unique_edges)

        self.unique_base_edges = list(unique_edges.values())

    def _add_facet(self, line, unique_edges):
        buf = line.split()
        size = int(buf.pop(0))
        vertex_numbers = [int(n) - 1 for n in buf]

        base_vertexes = [self.base_vertexes[n] for n in vertex_numbers]
        vertexes = [self.vertexes[n] for n in vertex_numbers]

        for n in range(size):
            self.edges.append(Edge(vertexes[n - 1], vertexes[n]))
            self._add_unique_base_edge(vertex_numbers, base_vertexes, n,
                                       unique_edges)

        self.facets.append(Facet(vertexes))
        self.base_facets.append(Facet(base_vertexes))

    @staticmethod
    def _add_unique_base_edge(vertex_numbers, base_vertexes, n, unique_edges):
        beg_number = vertex_numbers[n - 1]
        fin_number = vertex_numbers[n]
        key = tuple(sorted((beg_number, fin_number)))
        if key not in unique_edges:
            unique_edges[key] = Edge(base_vertexes[n - 1], base_vertexes[n])

    @classmethod
    def _edge_satisfies_characteristic_conditions(cls, edge):
        return (
            edge.is_fully_invisible()
            and edge.angle_with_horizontal() <= cls.MAX_ANGLE
            and edge.projected_center_distance_to_x2()
            < cls.MAX_CENTER_DISTANCE
        )

    def hidden_edge_projection_sum(self):
        total = 0.0
        for source_edge in self.unique_base_edges:
            edge = source_edge.clone()
            for facet in self.base_facets:
                edge.shadow(facet)
            if self._edge_satisfies_characteristic_conditions(edge):
                total += edge.projection_length()
        return total

    def print_hidden_edge_projection_sum(self):
        print(
            "Характеристика полиэдра: "
            f"{self.hidden_edge_projection_sum()}",
        )

    def draw(self, tk):  # pragma: no cover
        tk.clean()
        for e in self.edges:
            e.reset_gaps()
            for f in self.facets:
                e.shadow(f)
            for s in e.gaps:
                tk.draw_line(e.r3(s.beg), e.r3(s.fin))
