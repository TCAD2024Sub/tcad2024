#include "stage3_sa_sw.hpp"

Stage3SaSw::Stage3SaSw()
{
    this->flag = true;
}

void Stage3SaSw::compute(ST2_OUT st2_input, W st3_wb, int (&n2c)[N_THREADS][N_CELLS])
{
    this->old_output.th_idx = this->new_output.th_idx;
    this->old_output.th_valid = this->new_output.th_valid;
    this->old_output.cell_a = this->new_output.cell_a;
    this->old_output.cell_b = this->new_output.cell_b;
    this->old_output.cva[0] = this->new_output.cva[0];
    this->old_output.cva[1] = this->new_output.cva[1];
    this->old_output.cva[2] = this->new_output.cva[2];
    this->old_output.cva[3] = this->new_output.cva[3];
    this->old_output.cvb[0] = this->new_output.cvb[0];
    this->old_output.cvb[1] = this->new_output.cvb[1];
    this->old_output.cvb[2] = this->new_output.cvb[2];
    this->old_output.cvb[3] = this->new_output.cvb[3];
    this->old_output.sw.th_idx = this->new_output.sw.th_idx;
    this->old_output.sw.th_valid = this->new_output.sw.th_valid;
    this->old_output.sw.sw = this->new_output.sw.sw;
    this->old_output.wa.th_idx = this->new_output.wa.th_idx;
    this->old_output.wa.cell = this->new_output.wa.cell;
    this->old_output.wa.node = this->new_output.wa.node;
    this->old_output.wb.th_idx = this->new_output.wb.th_idx;
    this->old_output.wb.cell = this->new_output.wb.cell;
    this->old_output.wb.node = this->new_output.wb.node;

    int st2_th_idx = st2_input.th_idx;
    bool st2_th_valid = st2_input.th_valid;
    int st2_cell_a = st2_input.cell_a;
    int st2_cell_b = st2_input.cell_b;
    int *st2_va = st2_input.va;
    int *st2_vb = st2_input.vb;
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

    if (st2_th_idx == 0 && st2_th_valid)
    {
        int a = 1;
    }

    bool usw = new_output.sw.sw;
    W uwa{};
    W uwb{};
    uwa.th_idx = this->new_output.wa.th_idx;
    uwa.cell = this->new_output.wa.cell;
    uwa.node = this->new_output.wa.node;
    uwb.th_idx = st3_wb.th_idx;
    uwb.cell = st3_wb.cell;
    uwb.node = st3_wb.node;

    if (usw)
    {
        if (flag)
        {
            if (uwa.node != -1)
            {
                n2c[uwa.th_idx][uwa.node] = uwa.cell;
            }
            flag = !flag;
        }
        else
        {
            if (uwb.node != -1)
            {
                n2c[uwb.th_idx][uwb.node] = uwb.cell;
            }
            flag = !flag;
        }
    }

    int cva[N_NEIGH] = {-1, -1, -1, -1};
    int cvb[N_NEIGH] = {-1, -1, -1, -1};

    for (int n = 0; n < N_NEIGH; ++n)
    {
        if (st2_va[n] != -1)
        {
            cva[n] = n2c[st2_th_idx][st2_va[n]];
        }
        if (st2_vb[n] != -1)
        {
            cvb[n] = n2c[st2_th_idx][st2_vb[n]];
        }
    }

    this->new_output.th_idx = st2_th_idx;
    this->new_output.th_valid = st2_th_valid;
    this->new_output.cell_a = st2_cell_a;
    this->new_output.cell_b = st2_cell_b;
    this->new_output.cva[0] = cva[0];
    this->new_output.cva[1] = cva[1];
    this->new_output.cva[2] = cva[2];
    this->new_output.cva[3] = cva[3];
    this->new_output.cvb[0] = cvb[0];
    this->new_output.cvb[1] = cvb[1];
    this->new_output.cvb[2] = cvb[2];
    this->new_output.cvb[3] = cvb[3];
    this->new_output.sw.th_idx = st2_sw.th_idx;
    this->new_output.sw.th_valid = st2_sw.th_valid;
    this->new_output.sw.sw = st2_sw.sw;
    this->new_output.wa.th_idx = st2_wa.th_idx;
    this->new_output.wa.cell = st2_wa.cell;
    this->new_output.wa.node = st2_wa.node;
    this->new_output.wb.th_idx = st2_wb.th_idx;
    this->new_output.wb.cell = st2_wb.cell;
    this->new_output.wb.node = st2_wb.node;
}