class GraphPrune:
    @staticmethod
    def prune_nodes_level_0(vertexes:list,edges:list):
        has_father = {}
        out_vertexes = {}
        for vertex in vertexes:
            has_father[vertex] = 0
            out_vertexes[vertex] = []
        for (src,dst) in edges:
            has_father[dst] = 1
            out_vertexes[src].append(dst)
        for vertex,boolean in has_father.items():
            if not boolean:
                vertexes.remove(vertex)
                for neighboor in out_vertexes[vertex]:
                    edges.remove((vertex,neighboor))
        return vertexes,edges
    
    @staticmethod
    def prune_leaf_nodes(vertexes:list,edges:list):
        has_children = {}
        in_vertexes = {}

        for vertex in vertexes:
            has_children[vertex] = 0
            in_vertexes[vertex] = []

        for (src,dst) in edges:
            has_children[src] = 1
            in_vertexes[dst].append(src)

        for vertex,boolean in has_children.items():
            if not boolean:
                vertexes.remove(vertex)
                for neighboor in in_vertexes[vertex]:
                    edges.remove((neighboor,vertex))
        return vertexes,edges
    

