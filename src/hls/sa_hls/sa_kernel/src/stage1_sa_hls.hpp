#ifndef CPP_STAGE1_SA_HLS_H
#define CPP_STAGE1_SA_HLS_H

#include "fifo_sa_hls.hpp"

class Stage1SaHls
{
private:
    bool m_flag;
#ifdef ARRAY_INLINE
    ap_int<8> m_th_idx_offset[N_THREADS];
#endif

    FifoSaHls m_fifo_a;
    FifoSaHls m_fifo_b;

public:
    ST1_OUT m_new_output = {0, false, 0, 0, 0, 0, {0, false, false}, {0, 0, 0}, {0, 0, 0}};
    ST1_OUT m_old_output = {0, false, 0, 0, 0, 0, {0, false, false}, {0, 0, 0}, {0, 0, 0}};

    Stage1SaHls();

#ifdef ARRAY_INLINE
    void compute(ST0_OUT st0_input, ST9_OUT st9_sw, W st1_wb, ap_int<8> *c2n);
#else
    void compute(ST0_OUT st0_input, ST9_OUT st9_sw, W st1_wb, ap_int<8> **c2n);
#endif
};
#endif
