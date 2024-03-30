from random import choice


class Placement:
    @staticmethod
    def random_placement(vertexes: list[int], pes: list[tuple]) -> list[dict[int, tuple] | dict[tuple, int]]:
        assert len(vertexes) <= len(pes)
        placement_n2c = {}
        placement_c2n = {}
        free_pes = pes.copy()
        for pe in free_pes:
            placement_c2n[pe] = None
        for vertex in vertexes:
            pe = choice(free_pes)
            free_pes.remove(pe)
            placement_n2c[vertex] = pe
            placement_c2n[pe] = vertex
        return [placement_n2c, placement_c2n]
