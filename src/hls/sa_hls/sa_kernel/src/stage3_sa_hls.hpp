#ifndef CPP_STAGE3_SA_HLS_H
#define CPP_STAGE3_SA_HLS_H

#include "types_sa_hls.hpp"

class Stage3SaHls
{
private:
    bool m_flag;
#ifdef ARRAY_INLINE
    ap_int<8> m_th_idx_offset[N_THREADS];
#endif

public:
    ST3_OUT m_new_output = {0, false, 0, 0, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {0, false, false}, {0, 0, -1}, {0, 0, -1}};
    ST3_OUT m_old_output = {0, false, 0, 0, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {0, false, false}, {0, 0, -1}, {0, 0, -1}};

    Stage3SaHls();

#ifdef ARRAY_INLINE
    void compute(ST2_OUT st2_input, W st3_wb, ap_int<8> *n2c);
#else
    void compute(ST2_OUT st2_input, W st3_wb, ap_int<8> **n2c);
#endif
};
#endif
