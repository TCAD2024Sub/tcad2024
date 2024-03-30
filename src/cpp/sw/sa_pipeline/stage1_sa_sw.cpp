#include "stage1_sa_sw.hpp"

Stage1SaSw::Stage1SaSw()
{
    this->flag = true;
    this->fifo_a = new FifoSaSw();
    this->fifo_b = new FifoSaSw();
    for (int i = 0; i < N_THREADS - 2; i++)
    {
        W fifo_cell_a = {0, 0, -1};
        W fifo_cell_b = {0, 0, -1};
        this->fifo_a->enqueue(fifo_cell_a);
        this->fifo_b->enqueue(fifo_cell_b);
    }
}

void Stage1SaSw::compute(ST0_OUT st0_input, ST9_OUT st9_sw, W st1_wb, int (&c2n)[N_THREADS][N_CELLS])
{
    this->old_output.th_idx = this->new_output.th_idx;
    this->old_output.th_valid = this->new_output.th_valid;
    this->old_output.cell_a = this->new_output.cell_a;
    this->old_output.cell_b = this->new_output.cell_b;
    this->old_output.node_a = this->new_output.node_a;
    this->old_output.node_b = this->new_output.node_b;
    this->old_output.sw.th_idx = this->new_output.sw.th_idx;
    this->old_output.sw.th_valid = this->new_output.sw.th_valid;
    this->old_output.sw.sw = this->new_output.sw.sw;
    this->old_output.wa.th_idx = this->new_output.wa.th_idx;
    this->old_output.wa.cell = this->new_output.wa.cell;
    this->old_output.wa.node = this->new_output.wa.node;
    this->old_output.wb.th_idx = this->new_output.wb.th_idx;
    this->old_output.wb.cell = this->new_output.wb.cell;
    this->old_output.wb.node = this->new_output.wb.node;

    int st0_th_idx = st0_input.th_idx;
    bool st0_th_valid = st0_input.th_valid;
    int st0_cell_a = st0_input.cell_a;
    int st0_cell_b = st0_input.cell_b;

    if (st0_th_idx == 0 && st0_th_valid)
    {
        int a = 1;
    }

    if (st0_th_valid)
    {
        this->fifo_a->enqueue(W{this->new_output.th_idx, this->new_output.cell_a, this->new_output.node_b});
        this->fifo_b->enqueue(W{this->new_output.th_idx, this->new_output.cell_b, this->new_output.node_a});
    }

    W wa{};
    W wb{};
    if (st0_th_valid)
    {
        wa = this->fifo_a->dequeue();
        wb = this->fifo_b->dequeue();
    }
    else
    {
        wa.th_idx = this->new_output.wa.th_idx;
        wa.cell = this->new_output.wa.cell;
        wa.node = this->new_output.wa.node;
        wb.th_idx = this->new_output.wb.th_idx;
        wb.cell = this->new_output.wb.cell;
        wb.node = this->new_output.wb.node;
    }

    bool usw = this->new_output.sw.sw;
    W uwa{};
    W uwb{};
    uwa.th_idx = this->new_output.wa.th_idx;
    uwa.cell = this->new_output.wa.cell;
    uwa.node = this->new_output.wa.node;
    uwb.th_idx = st1_wb.th_idx;
    uwb.cell = st1_wb.cell;
    uwb.node = st1_wb.node;

    if (usw)
    {
        if (this->flag)
        {
            c2n[uwa.th_idx][uwa.cell] = wa.node;
            this->flag = !this->flag;
        }
        else
        {
            c2n[uwb.th_idx][uwb.cell] = uwb.node;
            this->flag = !this->flag;
        }
    }

    this->new_output.th_idx = st0_th_idx;
    this->new_output.th_valid = st0_th_valid;
    this->new_output.cell_a = st0_cell_a;
    this->new_output.cell_b = st0_cell_b;
    this->new_output.node_a = c2n[st0_th_idx][st0_cell_a];
    this->new_output.node_b = c2n[st0_th_idx][st0_cell_b];
    this->new_output.sw.th_idx = st9_sw.th_idx;
    this->new_output.sw.th_valid = st9_sw.th_valid;
    this->new_output.sw.sw = st9_sw.sw;
    this->new_output.wa.th_idx = wa.th_idx;
    this->new_output.wa.cell = wa.cell;
    this->new_output.wa.node = wa.node;
    this->new_output.wb.th_idx = wb.th_idx;
    this->new_output.wb.cell = wb.cell;
    this->new_output.wb.node = wb.node;
}