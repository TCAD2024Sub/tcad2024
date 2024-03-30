import cython


@cython.boundscheck(False)
@cython.wraparound(False)
class Stage10SA:
    """
    Tenth Pipe from SA_Verilog. This pipe generates a sync delay.
    """

    def __init__(self):
        """
        Initializes Stage10SA.
        """
        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'sw': False
        }
        self.old_output: dict = self.new_output.copy()

    def compute(self, st9_input: dict):
        """
        Computes sync delay.

        Args:
            st9_input (dict): Input dictionary containing 'th_idx', 'th_valid', and 'sw'.
        """
        # Move forward the ready outputs
        self.old_output = self.new_output.copy()

        st9_th_idx: cython.int = st9_input['th_idx']
        st9_th_valid: cython.bint = st9_input['th_valid']
        st9_sw: cython.bint = st9_input['sw']

        self.new_output: dict = {
            'th_idx': st9_th_idx,
            'th_valid': st9_th_valid,
            'sw': st9_sw
        }
