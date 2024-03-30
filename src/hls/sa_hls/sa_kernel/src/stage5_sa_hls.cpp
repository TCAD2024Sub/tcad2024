#include "stage5_sa_hls.hpp"

void Stage5SaHls::compute(ST4_OUT st4_input)
{
#ifdef PRAGMAS
#pragma HLS inline
#endif

    m_old_output.th_idx = m_new_output.th_idx;
    m_old_output.th_valid = m_new_output.th_valid;
    for (ap_int<8> i = 0; i < N_NEIGH / 2; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_old_output.dvac[i] = m_new_output.dvac[i];
        m_old_output.dvbc[i] = m_new_output.dvbc[i];
    }
    for (ap_int<8> i = 0; i < N_NEIGH; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_old_output.dvas[i] = m_new_output.dvas[i];
        m_old_output.dvbs[i] = m_new_output.dvbs[i];
    }

    ap_int<8> st4_th_idx = st4_input.th_idx;
    bool st4_th_valid = st4_input.th_valid;
    ap_int<8> st4_cbs = st4_input.cell_a;
    ap_int<8> st4_cas = st4_input.cell_b;

    ap_int<8> dvac[2] = {st4_input.dvac[0] + st4_input.dvac[1], st4_input.dvac[2] + st4_input.dvac[3]};
    ap_int<8> dvbc[2] = {st4_input.dvbc[0] + st4_input.dvbc[1], st4_input.dvbc[2] + st4_input.dvbc[3]};

    ap_int<8> dvas[N_NEIGH] = {0, 0, 0, 0};
    ap_int<8> dvbs[N_NEIGH] = {0, 0, 0, 0};

    for (ap_int<8> n = 0; n < N_NEIGH; ++n)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        ap_int<8> i1, i2, j1, j2;

        if (st4_input.cva[n] != -1)
        {
            get_line_column_from_cell(st4_cas, N_LINES, N_COLUMNS, i1, j1);
            if (st4_cas == st4_input.cva[n])
            {
                get_line_column_from_cell(st4_cbs, N_LINES, N_COLUMNS, i2, j2);
            }
            else
            {
                get_line_column_from_cell(st4_input.cva[n], N_LINES, N_COLUMNS, i2, j2);
            }
#if defined(ONE_HOP)
            dvas[n] = dist_one_hop(i1, j1, i2, j2);
#elif defined(MESH)
            dvas[n] = dist_manhattan(i1, j1, i2, j2);
#endif
        }

        if (st4_input.cvb[n] != -1)
        {
            get_line_column_from_cell(st4_cbs, N_LINES, N_COLUMNS, i1, j1);
            if (st4_cbs == st4_input.cvb[n])
            {
                get_line_column_from_cell(st4_cas, N_LINES, N_COLUMNS, i2, j2);
            }
            else
            {
                get_line_column_from_cell(st4_input.cvb[n], N_LINES, N_COLUMNS, i2, j2);
            }
#if defined(ONE_HOP)
            dvbs[n] = dist_one_hop(i1, j1, i2, j2);
#elif defined(MESH)
            dvbs[n] = dist_manhattan(i1, j1, i2, j2);
#endif
        }
    }

    m_new_output.th_idx = st4_th_idx;
    m_new_output.th_valid = st4_th_valid;
    for (ap_int<8> i = 0; i < N_NEIGH / 2; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_new_output.dvac[i] = dvac[i];
        m_new_output.dvbc[i] = dvbc[i];
    }
    for (ap_int<8> i = 0; i < N_NEIGH; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_new_output.dvas[i] = dvas[i];
        m_new_output.dvbs[i] = dvbs[i];
    }
}