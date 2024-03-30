import pygraphviz as pgv


class GraphExporter:
    @staticmethod
    def export_dot_graph(vertexes: list, edges, path, filename):
        graph = pgv.AGraph(directed=True)

        graph.add_nodes_from(vertexes)
        graph.add_edges_from(edges)
        path_graph = path + filename + '.dot'

        graph.write(path_graph)
        graph.draw(path + filename + '.png', format='png', prog='dot')
