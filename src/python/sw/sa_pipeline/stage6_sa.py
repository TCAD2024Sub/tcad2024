# cython: language_level=3
import cython


class Stage6SA:
    """
    Sixth Pipe from SA_Verilog. This pipe is responsible to execute the 2-2 
    additions for the distances found in the left pipe.
    """

    def __init__(self):
        """

        """
        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'dvac': 0,
            'dvbc': 0,
            'dvas': [0, 0],
            'dvbs': [0, 0]
        }
        self.old_output: dict = self.new_output.copy()

    def compute(self, st5_input: dict):
        """

        @param st5_input:
        """
        # moving forward the ready outputs
        self.old_output = self.new_output.copy()

        st5_th_idx: cython.int = st5_input['th_idx']
        st5_th_valid: cython.bint = st5_input['th_valid']

        # fixme only for debugging
        # if st5_th_idx == 0:
        #    z = 1

        st5_dvac: list[cython.int] = st5_input['dvac']
        st5_dvbc: list[cython.int] = st5_input['dvbc']
        st5_dvas: list[cython.int] = st5_input['dvas']
        st5_dvbs: list[cython.int] = st5_input['dvbs']

        dvac: cython.int = st5_dvac[0] + st5_dvac[1]
        dvbc: cython.int = st5_dvbc[0] + st5_dvbc[1]
        dvas: list[cython.int] = [st5_dvas[0] + st5_dvas[1], st5_dvas[2] + st5_dvas[3]]
        dvbs: list[cython.int] = [st5_dvbs[0] + st5_dvbs[1], st5_dvbs[2] + st5_dvbs[3]]

        self.new_output = {
            'th_idx': st5_th_idx,
            'th_valid': st5_th_valid,
            'dvac': dvac,
            'dvbc': dvbc,
            'dvas': dvas,
            'dvbs': dvbs
        }
