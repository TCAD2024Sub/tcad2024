#include "stage8_sa_hls.hpp"

void Stage8SaHls::compute(ST7_OUT st7_input)
{
#ifdef PRAGMAS
#pragma HLS inline
#endif

    m_old_output.th_idx = m_new_output.th_idx;
    m_old_output.th_valid = m_new_output.th_valid;
    m_old_output.dc = m_new_output.dc;
    m_old_output.ds = m_new_output.ds;

    ap_int<8> st7_th_idx = st7_input.th_idx;
    bool st7_th_valid = st7_input.th_valid;
    ap_int<8> st7_dc = st7_input.dc;

    ap_int<8> st7_dvas = st7_input.dvas;
    ap_int<8> st7_dvbs = st7_input.dvbs;

    ap_int<8> ds = st7_dvas + st7_dvbs;

    m_new_output.th_idx = st7_th_idx;
    m_new_output.th_valid = st7_th_valid;
    m_new_output.dc = st7_dc;
    m_new_output.ds = ds;
}
