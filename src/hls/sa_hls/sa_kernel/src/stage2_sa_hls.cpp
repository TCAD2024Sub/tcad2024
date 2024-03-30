#include "stage2_sa_hls.hpp"

#ifdef ARRAY_INLINE
void Stage2SaHls::compute(ST1_OUT st1_input, ap_int<8> *neighbors)
#else
void Stage2SaHls::compute(ST1_OUT st1_input, ap_int<8> **neighbors)
#endif
{
#ifdef PRAGMAS
#pragma HLS inline
#endif

    m_old_output.th_idx = m_new_output.th_idx;
    m_old_output.th_valid = m_new_output.th_valid;
    m_old_output.cell_a = m_new_output.cell_a;
    m_old_output.cell_b = m_new_output.cell_b;
    m_old_output.node_a = m_new_output.node_a;
    m_old_output.node_b = m_new_output.node_b;
    for (ap_int<8> i = 0; i < N_NEIGH; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_old_output.va[i] = m_new_output.va[i];
        m_old_output.vb[i] = m_new_output.vb[i];
    }

    m_old_output.sw.th_idx = m_new_output.sw.th_idx;
    m_old_output.sw.th_valid = m_new_output.sw.th_valid;
    m_old_output.sw.sw = m_new_output.sw.sw;
    m_old_output.wa.th_idx = m_new_output.wa.th_idx;
    m_old_output.wa.cell = m_new_output.wa.cell;
    m_old_output.wa.node = m_new_output.wa.node;
    m_old_output.wb.th_idx = m_new_output.wb.th_idx;
    m_old_output.wb.cell = m_new_output.wb.cell;
    m_old_output.wb.node = m_new_output.wb.node;

    ap_int<8> st1_th_idx = st1_input.th_idx;
    bool st1_th_valid = st1_input.th_valid;
    ap_int<8> st1_cell_a = st1_input.cell_a;
    ap_int<8> st1_cell_b = st1_input.cell_b;
    ap_int<8> st1_node_a = st1_input.node_a;
    ap_int<8> st1_node_b = st1_input.node_b;
    ST9_OUT st1_sw{};
    W st1_wa{};
    W st1_wb{};
    st1_sw.th_idx = st1_input.sw.th_idx;
    st1_sw.th_valid = st1_input.sw.th_valid;
    st1_sw.sw = st1_input.sw.sw;
    st1_wa.th_idx = st1_input.wa.th_idx;
    st1_wa.cell = st1_input.wa.cell;
    st1_wa.node = st1_input.wa.node;
    st1_wb.th_idx = st1_input.wb.th_idx;
    st1_wb.cell = st1_input.wb.cell;
    st1_wb.node = st1_input.wb.node;

    ap_int<8> va[N_NEIGH] = {-1, -1, -1, -1};
    ap_int<8> vb[N_NEIGH] = {-1, -1, -1, -1};

    if (st1_node_a != -1)
    {
        for (ap_int<8> n = 0; n < N_NEIGH; ++n)
        {
#ifdef PRAGMAS
#pragma HLS unroll
#endif

#ifdef ARRAY_INLINE
            ap_int<8> idx = (st1_node_a * N_NEIGH) + n;
            va[n] = neighbors[idx];
#else
            va[n] = neighbors[st1_node_a][n];
#endif
        }
    }
    
    if (st1_node_b != -1)
    {
        for (ap_int<8> n = 0; n < N_NEIGH; ++n)
        {
#ifdef PRAGMAS
#pragma HLS unroll
#endif

#ifdef ARRAY_INLINE
            ap_int<8> idx = (st1_node_b * N_NEIGH) + n;
            vb[n] = neighbors[idx];
#else
            vb[n] = neighbors[st1_node_b][n];
#endif
        }
    }
    m_new_output.th_idx = st1_th_idx;
    m_new_output.th_valid = st1_th_valid;
    m_new_output.cell_a = st1_cell_a;
    m_new_output.cell_b = st1_cell_b;
    m_new_output.node_a = st1_node_a;
    m_new_output.node_b = st1_node_b;
    for (ap_int<8> i = 0; i < N_NEIGH; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_new_output.va[i] = va[i];
        m_new_output.vb[i] = vb[i];
    }
    m_new_output.sw.th_idx = st1_sw.th_idx;
    m_new_output.sw.th_valid = st1_sw.th_valid;
    m_new_output.sw.sw = st1_sw.sw;
    m_new_output.wa.th_idx = st1_wa.th_idx;
    m_new_output.wa.cell = st1_wa.cell;
    m_new_output.wa.node = st1_wa.node;
    m_new_output.wb.th_idx = st1_wb.th_idx;
    m_new_output.wb.cell = st1_wb.cell;
    m_new_output.wb.node = st1_wb.node;
}
