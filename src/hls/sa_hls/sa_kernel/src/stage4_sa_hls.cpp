#include "stage4_sa_hls.hpp"

void Stage4SaHls::compute(ST3_OUT st3_input)
{
#ifdef PRAGMAS
#pragma HLS inline
#endif

    m_old_output = m_new_output;
    m_old_output = m_new_output;
    m_old_output = m_new_output;
    m_old_output = m_new_output;
    for (ap_int<8> i = 0; i < N_NEIGH; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_old_output.cva[i] = m_new_output.cva[i];
        m_old_output.cvb[i] = m_new_output.cvb[i];
        m_old_output.dvac[i] = m_new_output.dvac[i];
        m_old_output.dvbc[i] = m_new_output.dvbc[i];
    }

    ap_int<8> st3_th_idx = st3_input.th_idx;
    bool st3_th_valid = st3_input.th_valid;
    ap_int<8> st3_cell_a = st3_input.cell_a;
    ap_int<8> st3_cell_b = st3_input.cell_b;

    ap_int<8> dvac[4] = {0, 0, 0, 0};
    ap_int<8> dvbc[4] = {0, 0, 0, 0};

    ap_int<8> ca = st3_cell_a;
    ap_int<8> cb = st3_cell_b;

    for (ap_int<8> n = 0; n < N_NEIGH; ++n)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        ap_int<8> i1, i2, j1, j2;

        if (st3_input.cva[n] != -1)
        {
            get_line_column_from_cell(ca, N_LINES, N_COLUMNS, i1, j1);
            get_line_column_from_cell(st3_input.cva[n], N_LINES, N_COLUMNS, i2, j2);
#if defined(ONE_HOP)
            dvac[n] = dist_one_hop(i1, j1, i2, j2);
#elif defined(MESH)
            dvac[n] = dist_manhattan(i1, j1, i2, j2);
#endif
        }

        if (st3_input.cvb[n] != -1)
        {
            get_line_column_from_cell(cb, N_LINES, N_COLUMNS, i1, j1);
            get_line_column_from_cell(st3_input.cvb[n], N_LINES, N_COLUMNS, i2, j2);
#if defined(ONE_HOP)
            dvbc[n] = dist_one_hop(i1, j1, i2, j2);
#elif defined(MESH)
            dvbc[n] = dist_manhattan(i1, j1, i2, j2);
#endif
        }
    }

    m_new_output.th_idx = st3_th_idx;
    m_new_output.th_valid = st3_th_valid;
    m_new_output.cell_a = st3_cell_a;
    m_new_output.cell_b = st3_cell_b;
    for (ap_int<8> i = 0; i < N_NEIGH; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_new_output.cva[i] = st3_input.cva[i];
        m_new_output.cvb[i] = st3_input.cvb[i];
        m_new_output.dvac[i] = dvac[i];
        m_new_output.dvbc[i] = dvbc[i];
    }
}
