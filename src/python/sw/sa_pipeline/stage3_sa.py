# cython: language_level=3
import cython


class Stage3SA:
    """
    Third Pipe from SA_Verilog. This pipe is responsible to bring the neighbor's cell from each neighbor node.
    """

    def __init__(self, n2c: list[list[cython.int]], n_threads: cython.int):
        """

        @param n2c:
        @param n_threads:
        """
        self.n_threads: cython.int = n_threads
        self.n2c: list[list[cython.int]] = n2c
        self.flag: cython.bint = True
        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'cell_a': 0,
            'cell_b': 0,
            'cva': [-1, -1, -1, -1],
            'cvb': [-1, -1, -1, -1],
            'sw': {'th_idx': 0, 'th_valid': False, 'sw': False},
            'wa': {'th_idx': 0, 'cell': 0, 'node': -1},
            'wb': {'th_idx': 0, 'cell': 0, 'node': -1},
        }
        self.old_output: dict = self.new_output.copy()
        # self.print_matrix(0)

    def compute(self, st2_input: dict, st3_wb: dict):
        """

        @param st2_input:
        @param st3_wb:
        """
        # moving forward the ready outputs
        self.old_output = self.new_output.copy()

        st2_th_idx: cython.int = st2_input['th_idx']
        st2_th_valid: cython.bint = st2_input['th_valid']
        st2_cell_a: cython.int = st2_input['cell_a']
        st2_cell_b: cython.int = st2_input['cell_b']
        st2_sw: dict = st2_input['sw']
        st2_wa: dict = st2_input['wa']
        st2_wb: dict = st2_input['wb']
        st2_va: list[cython.int] = st2_input['va']
        st2_vb: list[cython.int] = st2_input['vb']

        # fixme only for debugging
        # if st2_th_idx == 0:
        #    z = 1

        # update memory
        usw: cython.bint = self.old_output['sw']['sw']
        uwa: dict = self.old_output['wa']
        uwb: dict = st3_wb
        if usw:
            if self.flag:
                if uwa['node'] != -1:
                    self.n2c[uwa['th_idx']][uwa['node']] = uwa['cell']
                self.flag = not self.flag
            else:
                if uwb['node'] != -1:
                    self.n2c[uwb['th_idx']][uwb['node']] = uwb['cell']
                self.flag = not self.flag

        cva: list[cython.int] = [-1, -1, -1, -1]
        cvb: list[cython.int] = [-1, -1, -1, -1]

        for i in range(len(st2_va)):
            if st2_va[i] != -1:
                cva[i] = self.n2c[st2_th_idx][st2_va[i]]
        for i in range(len(st2_vb)):
            if st2_vb[i] != -1:
                cvb[i] = self.n2c[st2_th_idx][st2_vb[i]]

        self.new_output = {
            'th_idx': st2_th_idx,
            'th_valid': st2_th_valid,
            'cell_a': st2_cell_a,
            'cell_b': st2_cell_b,
            'cva': cva,
            'cvb': cvb,
            'sw': st2_sw,
            'wa': st2_wa,
            'wb': st2_wb,
        }

    '''def print_matrix(self, idx: int):
        sqrt_ = ceil(sqrt(len(self.n2c[idx])))
        nidx = 0
        str_ = 'n2c_th:%d\n' % idx
        for i in range(sqrt_):
            for j in range(sqrt_):
                str_ += '%d ' % self.n2c[idx][nidx]
                nidx += 1
            str_ += '\n'
        print(str_)'''
