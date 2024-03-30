#include "stage3_sa_hls.hpp"

Stage3SaHls::Stage3SaHls()
{
    m_flag = true;
#ifdef ARRAY_INLINE
    for (ap_int<8> i = 0; i < N_THREADS; i++)
    {
        m_th_idx_offset[i] = i * N_CELLS;
    }
#endif
}

#ifdef ARRAY_INLINE
void Stage3SaHls::compute(ST2_OUT st2_input, W st3_wb, ap_int<8> *n2c)
#else
void Stage3SaHls::compute(ST2_OUT st2_input, W st3_wb, ap_int<8> **n2c)
#endif
{
#ifdef PRAGMAS
#pragma HLS inline
#endif

    m_old_output.th_idx = m_new_output.th_idx;
    m_old_output.th_valid = m_new_output.th_valid;
    m_old_output.cell_a = m_new_output.cell_a;
    m_old_output.cell_b = m_new_output.cell_b;
    for (ap_int<8> i = 0; i < N_NEIGH; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_old_output.cva[i] = m_new_output.cva[i];
        m_old_output.cvb[i] = m_new_output.cvb[i];
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

    ap_int<8> st2_th_idx = st2_input.th_idx;
    bool st2_th_valid = st2_input.th_valid;
    ap_int<8> st2_cell_a = st2_input.cell_a;
    ap_int<8> st2_cell_b = st2_input.cell_b;
    ap_int<8> *st2_va = st2_input.va;
    ap_int<8> *st2_vb = st2_input.vb;
    ST9_OUT st2_sw{};
    W st2_wa{};
    W st2_wb{};
    st2_sw.th_idx = st2_input.sw.th_idx;
    st2_sw.th_valid = st2_input.sw.th_valid;
    st2_sw.sw = st2_input.sw.sw;
    st2_wa.th_idx = st2_input.wa.th_idx;
    st2_wa.cell = st2_input.wa.cell;
    st2_wa.node = st2_input.wa.node;
    st2_wb.th_idx = st2_input.wb.th_idx;
    st2_wb.cell = st2_input.wb.cell;
    st2_wb.node = st2_input.wb.node;

    bool usw = m_new_output.sw.sw;
    W uwa{};
    W uwb{};
    uwa.th_idx = m_new_output.wa.th_idx;
    uwa.cell = m_new_output.wa.cell;
    uwa.node = m_new_output.wa.node;
    uwb.th_idx = st3_wb.th_idx;
    uwb.cell = st3_wb.cell;
    uwb.node = st3_wb.node;

    if (usw)
    {
        if (m_flag)
        {
            if (uwa.node != -1)
            {
#ifdef ARRAY_INLINE
                ap_int<8> idx = m_th_idx_offset[uwa.th_idx] + uwa.node;
                n2c[idx] = uwa.cell;
#else
                n2c[uwa.th_idx][uwa.node] = uwa.cell;
#endif
            }
        }
        else
        {
            if (uwb.node != -1)
            {
#ifdef ARRAY_INLINE
                ap_int<8> idx = m_th_idx_offset[uwb.th_idx] + uwb.node;
                n2c[idx] = uwb.cell;
#else
                n2c[uwb.th_idx][uwb.node] = uwb.cell;
#endif
            }
        }
        m_flag = !m_flag;
    }

    ap_int<8> cva[N_NEIGH] = {-1, -1, -1, -1};
    ap_int<8> cvb[N_NEIGH] = {-1, -1, -1, -1};

    for (ap_int<8> n = 0; n < N_NEIGH; ++n)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        if (st2_va[n] != -1)
        {
#ifdef ARRAY_INLINE
            ap_int<8> idx = m_th_idx_offset[st2_th_idx] + st2_va[n];
            if (n == 0)
                cva[n] = n2c[idx];
#else
            cva[n] = n2c[st2_th_idx][st2_va[n]];
#endif
        }
        if (st2_vb[n] != -1)
        {
#ifdef ARRAY_INLINE
            ap_int<8> idx = m_th_idx_offset[st2_th_idx] + st2_vb[n];
            cvb[n] = n2c[idx];
#else
            cvb[n] = n2c[st2_th_idx][st2_vb[n]];
#endif
        }
    }

    m_new_output.th_idx = st2_th_idx;
    m_new_output.th_valid = st2_th_valid;
    m_new_output.cell_a = st2_cell_a;
    m_new_output.cell_b = st2_cell_b;
    for (ap_int<8> i = 0; i < N_NEIGH; i++)
    {
#ifdef PRAGMAS
#pragma HLS unroll
#endif
        m_new_output.cva[i] = cva[i];
        m_new_output.cvb[i] = cvb[i];
    }

    m_new_output.sw.th_idx = st2_sw.th_idx;
    m_new_output.sw.th_valid = st2_sw.th_valid;
    m_new_output.sw.sw = st2_sw.sw;
    m_new_output.wa.th_idx = st2_wa.th_idx;
    m_new_output.wa.cell = st2_wa.cell;
    m_new_output.wa.node = st2_wa.node;
    m_new_output.wb.th_idx = st2_wb.th_idx;
    m_new_output.wb.cell = st2_wb.cell;
    m_new_output.wb.node = st2_wb.node;
}
