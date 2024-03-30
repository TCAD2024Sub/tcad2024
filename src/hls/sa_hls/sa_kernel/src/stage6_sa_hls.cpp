#include "stage6_sa_hls.hpp"

void Stage6SaHls::compute(ST5_OUT st5_input)
{
#ifdef PRAGMAS
#pragma HLS inline
#endif

    m_old_output.th_idx = m_new_output.th_idx;
    m_old_output.th_valid = m_new_output.th_valid;
    m_old_output.dvac = m_new_output.dvac;
    m_old_output.dvbc = m_new_output.dvbc;
    for (ap_int<8> i = 0; i < N_NEIGH / 2; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_old_output.dvas[i] = m_new_output.dvas[i];
        m_old_output.dvbs[i] = m_new_output.dvbs[i];
    }

    ap_int<8> st5_th_idx = st5_input.th_idx;
    bool st5_th_valid = st5_input.th_valid;

    ap_int<8> dvac = st5_input.dvac[0] + st5_input.dvac[1];
    ap_int<8> dvbc = st5_input.dvbc[0] + st5_input.dvbc[1];
    ap_int<8> dvas[2] = {st5_input.dvas[0] + st5_input.dvas[1], st5_input.dvas[2] + st5_input.dvas[3]};
    ap_int<8> dvbs[2] = {st5_input.dvbs[0] + st5_input.dvbs[1], st5_input.dvbs[2] + st5_input.dvbs[3]};

    m_new_output.th_idx = st5_th_idx;
    m_new_output.th_valid = st5_th_valid;
    m_new_output.dvac = dvac;
    m_new_output.dvbc = dvbc;
    for (ap_int<8> i = 0; i < N_NEIGH / 2; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_new_output.dvas[i] = dvas[i];
        m_new_output.dvbs[i] = dvbs[i];
    }
}