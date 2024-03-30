#include "stage4_sa_sw.hpp"

void Stage4SaSw::compute(ST3_OUT st3_input)
{
    this->old_output = this->new_output;
    this->old_output = this->new_output;
    this->old_output = this->new_output;
    this->old_output = this->new_output;
    this->old_output.cva[0] = this->new_output.cva[0];
    this->old_output.cva[1] = this->new_output.cva[1];
    this->old_output.cva[2] = this->new_output.cva[2];
    this->old_output.cva[3] = this->new_output.cva[3];
    this->old_output.cvb[0] = this->new_output.cvb[0];
    this->old_output.cvb[1] = this->new_output.cvb[1];
    this->old_output.cvb[2] = this->new_output.cvb[2];
    this->old_output.cvb[3] = this->new_output.cvb[3];
    this->old_output.dvac[0] = this->new_output.dvac[0];
    this->old_output.dvac[1] = this->new_output.dvac[1];
    this->old_output.dvac[2] = this->new_output.dvac[2];
    this->old_output.dvac[3] = this->new_output.dvac[3];
    this->old_output.dvbc[0] = this->new_output.dvbc[0];
    this->old_output.dvbc[1] = this->new_output.dvbc[1];
    this->old_output.dvbc[2] = this->new_output.dvbc[2];
    this->old_output.dvbc[3] = this->new_output.dvbc[3];

    int st3_th_idx = st3_input.th_idx;
    bool st3_th_valid = st3_input.th_valid;
    int st3_cell_a = st3_input.cell_a;
    int st3_cell_b = st3_input.cell_b;

    if (st3_th_idx == 0 && st3_th_valid)
    {
        int a = 1;
    }

    int dvac[4] = {0, 0, 0, 0};
    int dvbc[4] = {0, 0, 0, 0};

    int ca = st3_cell_a;
    int cb = st3_cell_b;

    for (int n = 0; n < N_NEIGH; ++n)
    {

        int i1, i2, j1, j2;

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

    this->new_output.th_idx = st3_th_idx;
    this->new_output.th_valid = st3_th_valid;
    this->new_output.cell_a = st3_cell_a;
    this->new_output.cell_b = st3_cell_b;
    this->new_output.cva[0] = st3_input.cva[0];
    this->new_output.cva[1] = st3_input.cva[1];
    this->new_output.cva[2] = st3_input.cva[2];
    this->new_output.cva[3] = st3_input.cva[3];
    this->new_output.cvb[0] = st3_input.cvb[0];
    this->new_output.cvb[1] = st3_input.cvb[1];
    this->new_output.cvb[2] = st3_input.cvb[2];
    this->new_output.cvb[3] = st3_input.cvb[3];
    this->new_output.dvac[0] = dvac[0];
    this->new_output.dvac[1] = dvac[1];
    this->new_output.dvac[2] = dvac[2];
    this->new_output.dvac[3] = dvac[3];
    this->new_output.dvbc[0] = dvbc[0];
    this->new_output.dvbc[1] = dvbc[1];
    this->new_output.dvbc[2] = dvbc[2];
    this->new_output.dvbc[3] = dvbc[3];
}
