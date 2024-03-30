from src.python.util.per_enum import ArchType
from src.python.util.util import Util


class Stage6YOTT:
    def __init__(self, arch_type: ArchType):
        """

        @param arch_type:
        @type arch_type:
        """
        self.arch_type: ArchType = arch_type
        self.new_output: dict = {
            'thread_index': 0,
            'thread_valid': 0,
            'B': 0,
            'cost': 0,
            'C_S': [0, 1],
            'dist_CA_CS': 1
        }
        self.old_output: dict = self.new_output

    def compute(self, stage5, num_annotations):
        """
        @param stage5:
        @type stage5:
        """

        self.old_output = self.new_output.copy()

        out_previous_stage: dict = stage5.old_output

        thread_index = out_previous_stage['thread_index']
        b = out_previous_stage['B']
        cs_c = out_previous_stage['Cs_C']
        dist_csb = out_previous_stage['dist_CsB']
        c_s = out_previous_stage['C_S']
        cost = self.calc_total_cost(c_s, cs_c, dist_csb, self.arch_type, num_annotations)

        self.new_output = {
            'thread_index': thread_index,
            'thread_valid': out_previous_stage['thread_valid'],
            'cost': cost,
            'C_S': c_s,
            'B': b,
            'dist_CA_CS': out_previous_stage['dist_CA_CS']
        }

    def calc_total_cost(self, c_s: list, cs_c: list, dist_cs_b: int, arch_type: ArchType, num_annotations: int):
        return sum([self.calc_cost(c_s, c_c, dist_c_b, arch_type) if (dist_c_b != -1 and i < num_annotations) else 0 for
                    i, (c_c, dist_c_b) in enumerate(zip(cs_c, dist_cs_b))])

    def calc_cost(self, c_s: list, c_c: list, dist_c_b: int, arch_type: ArchType) -> int:
        """
        @param c_s: 
        @type c_s: 
        @param c_c: 
        @type c_c: 
        @param dist_c_b: annotation
        @type dist_c_b: 
        @param arch_type: 
        @type arch_type: 
        @return: 
        @rtype: 
        """
        return abs(Util.calc_dist(c_s, c_c, arch_type) - dist_c_b)
