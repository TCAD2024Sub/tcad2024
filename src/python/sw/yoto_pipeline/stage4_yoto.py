from src.python.util.util import Util


class Stage4YOTO(object):
    """
    This class is responsible decide if the 'b' can b placed in the proposed cell
    and send to other stages the update signal
    """

    def __init__(self, c2n: list[list[list]], n_cells_sqrt: int):
        self.n_cells_sqrt: int = n_cells_sqrt
        self.c2n: list[list[list]] = c2n

        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'place': False,
            'dist_counter': 0,
            'b': 0,
            'ib': 0,
            'jb': 0,
        }

        self.old_output: dict = self.new_output.copy()

    def compute(self, st3_input: dict, st4_input: dict):
        # Move forward the output
        self.old_output = self.new_output.copy()

        # return update
        st4_th_idx: int = st4_input['th_idx']
        st4_place: bool = st4_input['place']
        st4_ib: int = st4_input['ib']
        st4_jb: int = st4_input['jb']
        st4_b: int = st4_input['b']
        if st4_place:
            self.c2n[st4_th_idx][st4_ib][st4_jb] = st4_b
            # for l in self.c2n[st4_th_idx]:
            # print(l)pass
            # print()

        # process the new output
        st3_th_idx: int = st3_input['th_idx']
        st3_th_valid: bool = st3_input['th_valid']
        st3_ib: int = st3_input['ib']
        st3_jb: int = st3_input['jb']
        st3_dist_counter: int = st3_input['dist_counter']
        st3_b: int = st3_input['b']

        place: bool = False

        out_of_border = Util.is_out_of_border_sqr(st3_ib, st3_jb, self.n_cells_sqrt)

        cb_content = 0 if out_of_border else self.c2n[st3_th_idx][st3_ib][st3_jb]

        if st3_th_valid and cb_content is None and not out_of_border:
            place = True

        if st3_b == 10:
            z=1

        self.new_output = {
            'th_idx': st3_th_idx,
            'th_valid': st3_th_valid,
            'place': place,
            'dist_counter': st3_dist_counter,
            'b': st3_b,
            'ib': st3_ib,
            'jb': st3_jb,
        }
