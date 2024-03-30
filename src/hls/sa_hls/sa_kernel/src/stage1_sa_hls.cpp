#include "stage1_sa_hls.hpp"

Stage1SaHls::Stage1SaHls()
{
    m_flag = true;
    for (ap_int<8> i = 0; i < N_THREADS - 2; i++)
    {
        W fifo_cell_a = {0, 0, -1};
        W fifo_cell_b = {0, 0, -1};
        m_fifo_a.enqueue(fifo_cell_a);
        m_fifo_b.enqueue(fifo_cell_b);
    }
#ifdef ARRAY_INLINE
    for (ap_int<8> i = 0; i < N_THREADS; i++)
    {
        m_th_idx_offset[i] = i * N_CELLS;
    }
#endif
}

#ifdef ARRAY_INLINE
void Stage1SaHls::compute(ST0_OUT st0_input, ST9_OUT st9_sw, W st1_wb, ap_int<8> *c2n)
#else
void Stage1SaHls::compute(ST0_OUT st0_input, ST9_OUT st9_sw, W st1_wb, ap_int<8> **c2n)
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
    m_old_output.sw.th_idx = m_new_output.sw.th_idx;
    m_old_output.sw.th_valid = m_new_output.sw.th_valid;
    m_old_output.sw.sw = m_new_output.sw.sw;
    m_old_output.wa.th_idx = m_new_output.wa.th_idx;
    m_old_output.wa.cell = m_new_output.wa.cell;
    m_old_output.wa.node = m_new_output.wa.node;
    m_old_output.wb.th_idx = m_new_output.wb.th_idx;
    m_old_output.wb.cell = m_new_output.wb.cell;
    m_old_output.wb.node = m_new_output.wb.node;

    ap_int<8> st0_th_idx = st0_input.th_idx;
    bool st0_th_valid = st0_input.th_valid;
    ap_int<8> st0_cell_a = st0_input.cell_a;
    ap_int<8> st0_cell_b = st0_input.cell_b;

    if (st0_th_valid)
    {
        m_fifo_a.enqueue(W{m_new_output.th_idx, m_new_output.cell_a, m_new_output.node_b});
        m_fifo_b.enqueue(W{m_new_output.th_idx, m_new_output.cell_b, m_new_output.node_a});
    }

    W wa{};
    W wb{};
    if (st0_th_valid)
    {
        wa = m_fifo_a.dequeue();
        wb = m_fifo_b.dequeue();
    }
    else
    {
        wa.th_idx = m_new_output.wa.th_idx;
        wa.cell = m_new_output.wa.cell;
        wa.node = m_new_output.wa.node;
        wb.th_idx = m_new_output.wb.th_idx;
        wb.cell = m_new_output.wb.cell;
        wb.node = m_new_output.wb.node;
    }

    bool usw = m_new_output.sw.sw;
    W uwa{};
    W uwb{};
    uwa.th_idx = m_new_output.wa.th_idx;
    uwa.cell = m_new_output.wa.cell;
    uwa.node = m_new_output.wa.node;
    uwb.th_idx = st1_wb.th_idx;
    uwb.cell = st1_wb.cell;
    uwb.node = st1_wb.node;

    if (usw)
    {
        if (m_flag)
        {
#ifdef ARRAY_INLINE
            ap_int<8> idx = m_th_idx_offset[uwa.th_idx] + uwa.cell;
            c2n[idx] = wa.node;
#else
            c2n[uwa.th_idx][uwa.cell] = wa.node;
#endif
        }
        else
        {
#ifdef ARRAY_INLINE
            ap_int<8> idx = m_th_idx_offset[uwb.th_idx] + uwb.cell;
            c2n[idx] = uwb.node;
#else
            c2n[uwb.th_idx][uwa.cell] = uwb.node;
#endif
        }
        m_flag = !m_flag;
    }

    m_new_output.th_idx = st0_th_idx;
    m_new_output.th_valid = st0_th_valid;
    m_new_output.cell_a = st0_cell_a;
    m_new_output.cell_b = st0_cell_b;
#ifdef ARRAY_INLINE
    ap_int<8> idxa = m_th_idx_offset[st0_th_idx] + st0_cell_a;
    ap_int<8> idxb = m_th_idx_offset[st0_th_idx] + st0_cell_b;
    m_new_output.node_a = c2n[idxa];
    m_new_output.node_b = c2n[idxb];
#else
    m_new_output.node_a = c2n[st0_th_idx][st0_cell_a];
    m_new_output.node_b = c2n[st0_th_idx][st0_cell_b];
#endif
    m_new_output.sw.th_idx = st9_sw.th_idx;
    m_new_output.sw.th_valid = st9_sw.th_valid;
    m_new_output.sw.sw = st9_sw.sw;
    m_new_output.wa.th_idx = wa.th_idx;
    m_new_output.wa.cell = wa.cell;
    m_new_output.wa.node = wa.node;
    m_new_output.wb.th_idx = wb.th_idx;
    m_new_output.wb.cell = wb.cell;
    m_new_output.wb.node = wb.node;
}
