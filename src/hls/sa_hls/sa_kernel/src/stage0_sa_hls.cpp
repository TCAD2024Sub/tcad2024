#include "stage0_sa_hls.hpp"

void Stage0SaHls::compute()
{
#ifdef PRAGMAS
#pragma HLS inline
#endif

    ap_int<8> th_idx_c = m_th_idx;

    m_old_output.th_idx = m_new_output.th_idx;
    m_old_output.th_valid = m_new_output.th_valid;
    m_old_output.cell_a = m_new_output.cell_a;
    m_old_output.cell_b = m_new_output.cell_b;

    if (!m_th_valid[th_idx_c])
    {
        if (m_cell_a[th_idx_c] == N_CELLS - 1)
        {
            m_cell_a[th_idx_c] = 0;
            if (m_cell_b[th_idx_c] == N_CELLS - 1)
            {
                m_cell_b[th_idx_c] = 0;
            }
            else
            {
                m_cell_b[th_idx_c] += 1;
            }
        }
        else
        {
            m_cell_a[th_idx_c] += 1;
        }

        m_th_idx += 1;
        if (m_th_idx == N_THREADS)
        {
            m_th_idx = 0;
        }
    }
    m_th_valid[th_idx_c] = !m_th_valid[th_idx_c];

    th_idx_c = m_th_idx;
    m_new_output.th_idx = m_th_idx;
    m_new_output.th_valid = m_th_valid[th_idx_c];
    m_new_output.cell_a = m_cell_a[th_idx_c];
    m_new_output.cell_b = m_cell_b[th_idx_c];

    if (m_th_valid[th_idx_c] && m_th_idx == 0)
    {
        m_exec_counter += 1;
    }
}
