# cython: language_level=3
import cython


class Stage8SA:
    """
    Eighth Pipe from SA_Verilog. This pipe is responsible to execute the 2-2 
    additions for the distances found in the left pipe.
    """

    def __init__(self):
        """

        """
        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'dc': 0,
            'ds': 0
        }
        self.old_output: dict = self.new_output.copy()

    def compute(self, st7_input: dict):
        """

        @param st7_input:
        """
        # moving forward the ready outputs
        self.old_output = self.new_output.copy()

        st7_th_idx: cython.int = st7_input['th_idx']
        st7_th_valid: cython.bint = st7_input['th_valid']
        st7_dc: cython.int = st7_input['dc']

        # fixme only for debugging
        # if st7_th_idx == 0:
        #    z = 1

        st7_dvas: cython.int = st7_input['dvas']
        st7_dvbs: cython.int = st7_input['dvbs']

        ds: cython.int = st7_dvas + st7_dvbs

        self.new_output: dict = {
            'th_idx': st7_th_idx,
            'th_valid': st7_th_valid,
            'dc': st7_dc,
            'ds': ds
        }
