# cython: language_level=3
import cython


class Stage2SA:
    """
    Second Pipe from SA_Verilog. This pipe is responsible to bring the neighbor from each node selected in the left
    pipe in the graph.
    """

    def __init__(self, neighbors: dict):
        """

        @param neighbors:
        """
        self.neighbors: dict = neighbors
        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'cell_a': 0,
            'cell_b': 0,
            'node_a': 0,
            'node_b': 0,
            'va': [-1, -1, -1, -1],
            'vb': [-1, -1, -1, -1],
            'sw': {'th_idx': 0, 'th_valid': False, 'sw': False},
            'wa': {'th_idx': 0, 'cell': 0, 'node': -1},
            'wb': {'th_idx': 0, 'cell': 0, 'node': -1},
        }
        self.old_output: dict = self.new_output.copy()

    def compute(self, st1_input: dict):
        """

        @param st1_input:
        """
        # moving forward the ready outputs
        self.old_output = self.new_output.copy()

        st1_th_idx: cython.int = st1_input['th_idx']
        st1_th_valid: cython.bint = st1_input['th_valid']
        st1_cell_a: cython.int = st1_input['cell_a']
        st1_cell_b: cython.int = st1_input['cell_b']
        st1_node_a: cython.int = st1_input['node_a']
        st1_node_b: cython.int = st1_input['node_b']
        st1_sw: dict = st1_input['sw']
        st1_wa: dict = st1_input['wa']
        st1_wb: dict = st1_input['wb']

        # fixme only for debugging
        # if st1_th_idx == 0:
        #    z = 1

        va: list[cython.int] = [-1, -1, -1, -1]
        vb: list[cython.int] = [-1, -1, -1, -1]

        if st1_node_a != -1:
            for i in range(len(self.neighbors[st1_node_a])):
                va[i] = self.neighbors[st1_node_a][i]
        if st1_node_b != -1:
            for i in range(len(self.neighbors[st1_node_b])):
                vb[i] = self.neighbors[st1_node_b][i]

        # reading pipe inputs
        self.new_output = {
            'th_idx': st1_th_idx,
            'th_valid': st1_th_valid,
            'cell_a': st1_cell_a,
            'cell_b': st1_cell_b,
            'node_a': st1_node_a,
            'node_b': st1_node_b,
            'va': va,
            'vb': vb,
            'sw': st1_sw,
            'wa': st1_wa,
            'wb': st1_wb
        }
