from src.python.util.per_graph import PeRGraph


class Stage2YOTT:
    def __init__(self, itl: list[list], per: PeRGraph, annotations: list[dict], num_threads: int, distance_table_bits):
        """

        @param itl:
        @type itl:
        @param per:
        @type per:
        @param annotations:
        @type annotations:
        @param num_threads:
        @type num_threads:
        """
        super().__init__()
        self.threads_edges = itl
        self.len_edges = len(itl)
        self.num_threads = num_threads
        self.annotations = annotations
        self.per = per
        self.dist_table_mask: int = pow(2, distance_table_bits) - 1

        self.new_output = {
            'thread_index': 0,
            'thread_valid': 0,
            'A': 0,
            'B': 0,
            'Cs': [-1, -1, -1],
            'dist_CsB': [-1, -1, -1],
            'index_list_edge': 0

        }

        self.old_output = self.new_output

    def compute(self, stage1, num_annotations):
        """

        @param stage1:
        @type stage1:
        """
        self.old_output = self.new_output.copy()
        out_previous_stage = stage1.old_output
        thread_index = out_previous_stage['thread_index']
        edge_index = out_previous_stage['edge_index']
        a, b = self.threads_edges[thread_index][edge_index]

        # fixme Método de anotações acrescentar 1 nas distâncias anotadas pra manter o padrão e ccorriir stage2_yott
        annotations = list(self.annotations[thread_index].values())[edge_index]
        while len(annotations) < num_annotations:
            annotations.append([-1, -1])

        annotations = annotations[0:3]
        # fixme Corrigir em traversal para que as anotações fiquem em inteiro
        annotations = [(self.per.nodes_to_idx[annotation[0]], annotation[1] + 1) if (
                    annotation[0] != -1 and annotation[1] < 3) else [-1, -1] for annotation in annotations]

        cs = []
        dist_cs_b = []

        for (c, dist_c_b) in annotations:
            cs.append(c)
            dist_cs_b.append(dist_c_b)

        index_list_edge = (thread_index ^ edge_index) & self.dist_table_mask

        self.new_output = {
            'thread_index': thread_index,
            'thread_valid': out_previous_stage['thread_valid'],
            'A': a,
            'B': b,
            'Cs': cs,
            'dist_CsB': dist_cs_b,
            'index_list_edge': index_list_edge
        }
