#ifndef CPP_STAGE0_SA_HLS_H
#define CPP_STAGE0_SA_HLS_H

#include "defines_sa_hls.hpp"
#include "types_sa_hls.hpp"

class Stage0SaHls
{
private:
    ap_int<8> m_cell_a[N_THREADS] = {0, 0, 0, 0, 0, 0};
    ap_int<8> m_cell_b[N_THREADS] = {0, 0, 0, 0, 0, 0};
    bool m_th_valid[N_THREADS] = {true, true, true, true, true, true};
    ap_int<8> m_th_idx = 0;
    int m_exec_counter = 0;

public:
    ST0_OUT m_new_output{0, true, 0, 0};
    ST0_OUT m_old_output{0, true, 0, 0};

    void compute();
};
#endif