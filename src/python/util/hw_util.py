from veriloggen import *


class HwUtil(object):
    """
        Utility class for hardware-related operations.
    """
    _instance = None

    @classmethod
    def instance(cls) -> 'HwUtil':
        """
        Returns the singleton instance of the HwUtil class.

        Returns:
            HwUtil: The singleton instance of HwUtil.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        pass

    @staticmethod
    def initialize_regs(module: Module, values=None):
        """
                Initializes registers in a Verilog module.

                Args:
                    module (Module): The Verilog module containing registers to initialize.
                    values (dict, optional): Dictionary containing initial values for registers. Defaults to None.
        """
        regs = []
        if values is None:
            values = {}
        flag = False
        for r in module.get_vars().items():
            if module.is_reg(r[0]):
                regs.append(r)
                if r[1].dims:
                    flag = True

        if len(regs) > 0:
            if flag:
                i = module.Integer("i_initial")
            s = module.Initial()
            for r in regs:
                if values:
                    if r[0] in values.keys():
                        value = values[r[0]]
                    else:
                        value = 0
                else:
                    value = 0
                if r[1].dims:
                    gen_for = For(i(0), i < r[1].dims[0], i.inc())(r[1][i](value))
                    s.add(gen_for)
                else:
                    s.add(r[1](value))
