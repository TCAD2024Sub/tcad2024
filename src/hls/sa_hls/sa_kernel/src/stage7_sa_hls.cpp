#include "stage7_sa_hls.hpp"

void Stage7SaHls::compute(ST6_OUT st6_input)
{
#ifdef PRAGMAS
#pragma HLS inline
#endif

    m_old_output.th_idx = m_new_output.th_idx;
    m_old_output.th_valid = m_new_output.th_valid;
    m_old_output.dc = m_new_output.dc;
    m_old_output.dvas = m_new_output.dvas;
    m_old_output.dvbs = m_new_output.dvbs;

    ap_int<8> st6_th_idx = st6_input.th_idx;
    bool st6_th_valid = st6_input.th_valid;
    ap_int<8> st6_dvac = st6_input.dvac;
    ap_int<8> st6_dvbc = st6_input.dvbc;

    ap_int<8> dc = st6_dvac + st6_dvbc;
    ap_int<8> dvas = st6_input.dvas[0] + st6_input.dvas[1];
    ap_int<8> dvbs = st6_input.dvbs[0] + st6_input.dvbs[1];

    m_new_output.th_idx = st6_th_idx;
    m_new_output.th_valid = st6_th_valid;
    m_new_output.dc = dc;
    m_new_output.dvas = dvas;
    m_new_output.dvbs = dvbs;
}