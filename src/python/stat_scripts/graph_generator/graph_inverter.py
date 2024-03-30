class GraphInverter:
    @staticmethod
    def invert_graph(edges: list[tuple[int, int]]):
        new_edges = []
        for (src, dst) in edges:
            new_edges.append((dst, src))
        return new_edges
