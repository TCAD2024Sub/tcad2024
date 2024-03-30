#ifndef CPP_STAGE2_SA_SW_H
#define CPP_STAGE2_SA_SW_H

#include "types_sa_sw.hpp"

class Stage2SaSw
{
private:
public:
    ST2_OUT new_output = {0, false, 0, 0, 0, 0, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {0, false, false}, {0, 0, -1}, {0, 0, -1}};
    ST2_OUT old_output = {0, false, 0, 0, 0, 0, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {0, false, false}, {0, 0, -1}, {0, 0, -1}};

    void compute(ST1_OUT st1_input, int (&neighbors)[N_CELLS][N_NEIGH]);
};
#endif