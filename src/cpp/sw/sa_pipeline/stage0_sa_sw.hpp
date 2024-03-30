#ifndef CPP_STAGE0_SA_SW_H
#define CPP_STAGE0_SA_SW_H

#include "defines_sa_sw.hpp"
#include "types_sa_sw.hpp"

class Stage0SaSw
{
private:
    int cell_a[N_THREADS] = {0, 0, 0, 0, 0, 0};
    int cell_b[N_THREADS] = {0, 0, 0, 0, 0, 0};
    bool th_valid[N_THREADS] = {true, true, true, true, true, true};
    int th_idx = 0;
    int exec_counter = 0;

public:
    ST0_OUT new_output{0, true, 0, 0};
    ST0_OUT old_output{0, true, 0, 0};

    void compute();
};
#endif