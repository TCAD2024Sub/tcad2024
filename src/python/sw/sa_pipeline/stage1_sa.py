# cython: language_level=3
import cython


class Stage1SA:
    """
    First Pipe from SA_Verilog. This pipe is responsible to search the content of the two cells selected by threads
    """

    def __init__(self, c2n: list[list[cython.int]], n_threads: cython.int):
        self.c2n: list[list[cython.int]] = c2n
        self.n_threads: cython.int = n_threads
        self.fifo_a: list[dict] = [{'th_idx': 0, 'cell': 0, 'node': -1}
                                   for _ in range(self.n_threads - 2)]
        self.fifo_b: list[dict] = [{'th_idx': 0, 'cell': 0, 'node': -1}
                                   for _ in range(self.n_threads - 2)]
        self.flag: cython.bint = True

        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'cell_a': 0,
            'cell_b': 0,
            'node_a': 0,
            'node_b': 0,
            'sw': {'th_idx': 0, 'th_valid': False, 'sw': False},
            'wa': {'th_idx': 0, 'cell': 0, 'node': 0},
            'wb': {'th_idx': 0, 'cell': 0, 'node': 0},
        }
        self.old_output: dict = self.new_output.copy()
        # self.print_matrix(0)

    # TODO update logic
    def compute(self, st0_input: dict, st9_sw: dict, st1_wb: dict):
        # moving forward the ready outputs
        self.old_output = self.new_output.copy()

        # reading pipe inputs
        st0_th_idx: cython.int = st0_input['th_idx']
        st0_th_valid: cython.bint = st0_input['th_valid']
        st0_cell_a: cython.int = st0_input['cell_a']
        st0_cell_b: cython.int = st0_input['cell_b']

        # fixme only for debugging
        # if st0_th_idx == 0:
        #    z = 1

        # enqueuing data
        if st0_th_valid:
            self.fifo_a.append(
                {'th_idx': self.new_output['th_idx'], 'cell': self.new_output['cell_a'],
                 'node': self.old_output['node_b']})
            self.fifo_b.append(
                {'th_idx': self.new_output['th_idx'], 'cell': self.new_output['cell_b'],
                 'node': self.new_output['node_a']})

        # Pop Queues
        wa: dict = self.new_output['wa']
        wb: dict = self.new_output['wb']
        if st0_th_valid:
            wa: dict = self.fifo_a.pop(0)
            wb: dict = self.fifo_b.pop(0)

        # update memory
        usw: cython.bint = self.new_output['sw']['sw']
        uwa: dict = self.new_output['wa']
        uwb: dict = st1_wb
        if usw:
            if self.flag:
                self.c2n[uwa['th_idx']][uwa['cell']] = wa['node']
                self.flag = not self.flag
            else:
                self.c2n[uwb['th_idx']][uwb['cell']] = uwb['node']
                self.flag = not self.flag
                if uwb['th_idx'] == 0:
                    pass
                    # self.print_matrix(uwb['th_idx'])

        self.new_output = {
            # fifos outputs ready to be moved forward
            'wa': wa,
            'wb': wb,
            'sw': st9_sw,

            # data ready to be moved forward
            'th_idx': st0_th_idx,
            'th_valid': st0_th_valid,
            'cell_a': st0_cell_a,
            'cell_b': st0_cell_b,

            # cell content ready to be moved forward
            'node_a': self.c2n[st0_th_idx][st0_cell_a],
            'node_b': self.c2n[st0_th_idx][st0_cell_b],
        }

    '''def print_matrix(self, idx: int):
        sqrt_ = ceil(sqrt(len(self.c2n[idx])))
        cell_idx = 0
        str_to_print = 'c2n_th:%d\n' % idx
        for i in range(sqrt_):
            for j in range(sqrt_):
                if self.c2n[idx][cell_idx] is None:
                    str_to_print += '   '
                else:
                    str_to_print += '%2d ' % self.c2n[idx][cell_idx]
                cell_idx += 1
            str_to_print += '\n'
        print(str_to_print)'''
