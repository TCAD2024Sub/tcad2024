# cython: language_level=3
import cython


class Stage9SA:
    """
    Ninth Pipe from SA_Verilog. This pipe is responsible to take the decision to do the swap or not.
    """

    def __init__(self):
        """

        """
        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'sw': False
        }
        self.old_output: dict = self.new_output.copy()

    def compute(self, st8_input: dict):
        """

        @param st8_input:
        """
        # moving forward the ready outputs
        self.old_output = self.new_output.copy()

        st8_th_idx: cython.int = st8_input['th_idx']
        st8_th_valid: cython.int = st8_input['th_valid']

        # fixme only for debugging
        # if st8_th_idx == 0 and st8_th_valid:
        #    z = 1

        st8_dc: cython.int = st8_input['dc']
        st8_ds: cython.int = st8_input['ds']

        sw: cython.bint = st8_ds < st8_dc
        # if sw:
        #    a = 1

        self.new_output: dict = {
            'th_idx': st8_th_idx,
            'th_valid': st8_th_valid,
            'sw': sw
        }

        '''if st8_th_idx == 0 and sw:
            # print(self.new_output)
            z = 1'''
