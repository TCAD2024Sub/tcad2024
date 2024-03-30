#include "stage9_sa_hls.hpp"

void Stage9SaHls::compute(ST8_OUT st8_input)
{
#ifdef PRAGMAS
#pragma HLS inline
#endif

    m_old_output.th_idx = m_new_output.th_idx;
    m_old_output.th_valid = m_new_output.th_valid;
    m_old_output.sw = m_new_output.sw;

    ap_int<8> st8_th_idx = st8_input.th_idx;
    bool st8_th_valid = st8_input.th_valid;
    ap_int<8> st8_dc = st8_input.dc;
    ap_int<8> st8_ds = st8_input.ds;

    bool sw_c = st8_ds < st8_dc;

    m_new_output.th_idx = st8_th_idx;
    m_new_output.th_valid = st8_th_valid;
    m_new_output.sw = sw_c;
}