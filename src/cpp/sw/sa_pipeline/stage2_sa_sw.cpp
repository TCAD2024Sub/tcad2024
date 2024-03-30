#include "stage2_sa_sw.hpp"

void Stage2SaSw::compute(ST1_OUT st1_input, int (&neighbors)[N_CELLS][N_NEIGH])
{

    this->old_output.th_idx = this->new_output.th_idx;
    this->old_output.th_valid = this->new_output.th_valid;
    this->old_output.cell_a = this->new_output.cell_a;
    this->old_output.cell_b = this->new_output.cell_b;
    this->old_output.node_a = this->new_output.node_a;
    this->old_output.node_b = this->new_output.node_b;
    this->old_output.va[0] = this->new_output.va[0];
    this->old_output.va[1] = this->new_output.va[1];
    this->old_output.va[2] = this->new_output.va[2];
    this->old_output.va[3] = this->new_output.va[3];
    this->old_output.vb[0] = this->new_output.vb[0];
    this->old_output.vb[1] = this->new_output.vb[1];
    this->old_output.vb[2] = this->new_output.vb[2];
    this->old_output.vb[3] = this->new_output.vb[3];
    this->old_output.sw.th_idx = this->new_output.sw.th_idx;
    this->old_output.sw.th_valid = this->new_output.sw.th_valid;
    this->old_output.sw.sw = this->new_output.sw.sw;
    this->old_output.wa.th_idx = this->new_output.wa.th_idx;
    this->old_output.wa.cell = this->new_output.wa.cell;
    this->old_output.wa.node = this->new_output.wa.node;
    this->old_output.wb.th_idx = this->new_output.wb.th_idx;
    this->old_output.wb.cell = this->new_output.wb.cell;
    this->old_output.wb.node = this->new_output.wb.node;

    int st1_th_idx = st1_input.th_idx;
    bool st1_th_valid = st1_input.th_valid;
    int st1_cell_a = st1_input.cell_a;
    int st1_cell_b = st1_input.cell_b;
    int st1_node_a = st1_input.node_a;
    int st1_node_b = st1_input.node_b;
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

    int va[N_NEIGH] = {-1, -1, -1, -1};
    int vb[N_NEIGH] = {-1, -1, -1, -1};

    if (st1_th_idx == 0 && st1_th_valid)
    {
        int a = 1;
    }

    if (st1_node_a != -1)
    {
        for (int n = 0; n < N_NEIGH; ++n)
        {
            va[n] = neighbors[st1_node_a][n];
        }
    }
    if (st1_node_b != -1)
    {
        for (int n = 0; n < 4; ++n)
        {
            vb[n] = neighbors[st1_node_b][n];
        }
    }
    this->new_output.th_idx = st1_th_idx;
    this->new_output.th_valid = st1_th_valid;
    this->new_output.cell_a = st1_cell_a;
    this->new_output.cell_b = st1_cell_b;
    this->new_output.node_a = st1_node_a;
    this->new_output.node_b = st1_node_b;
    this->new_output.va[0] = va[0];
    this->new_output.va[1] = va[1];
    this->new_output.va[2] = va[2];
    this->new_output.va[3] = va[3];
    this->new_output.vb[0] = vb[0];
    this->new_output.vb[1] = vb[1];
    this->new_output.vb[2] = vb[2];
    this->new_output.vb[3] = vb[3];
    this->new_output.sw.th_idx = st1_sw.th_idx;
    this->new_output.sw.th_valid = st1_sw.th_valid;
    this->new_output.sw.sw = st1_sw.sw;
    this->new_output.wa.th_idx = st1_wa.th_idx;
    this->new_output.wa.cell = st1_wa.cell;
    this->new_output.wa.node = st1_wa.node;
    this->new_output.wb.th_idx = st1_wb.th_idx;
    this->new_output.wb.cell = st1_wb.cell;
    this->new_output.wb.node = st1_wb.node;
}
