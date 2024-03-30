# cython: language_level=3
import cython


class Stage7SA:
    """
    Seventh Pipe from SA_Verilog. This pipe is responsible to execute the 2-2 
    additions for the distances found in the left pipe.
    """

    def __init__(self):
        """

        """
        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'dc': 0,
            'dvas': 0,
            'dvbs': 0
        }
        self.old_output: dict = self.new_output.copy()

    def compute(self, st6_input: dict):
        """

        @param st6_input:
        """
        # moving forward the ready outputs
        self.old_output = self.new_output.copy()

        st6_th_idx: cython.int = st6_input['th_idx']
        st6_th_valid: cython.bint = st6_input['th_valid']

        # fixme only for debugging
        # if st6_th_idx == 0:
        #    z = 1

        st6_dvac: cython.int = st6_input['dvac']
        st6_dvbc: cython.int = st6_input['dvbc']
        st6_dvas: list[cython.int] = st6_input['dvas']
        st6_dvbs: list[cython.int] = st6_input['dvbs']

        dc: cython.int = st6_dvac + st6_dvbc
        dvas: cython.int = st6_dvas[0] + st6_dvas[1]
        dvbs: cython.int = st6_dvbs[0] + st6_dvbs[1]

        self.new_output: dict = {
            'th_idx': st6_th_idx,
            'th_valid': st6_th_valid,
            'dc': dc,
            'dvas': dvas,
            'dvbs': dvbs
        }
