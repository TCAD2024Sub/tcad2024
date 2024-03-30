#include "stage5_sa_sw.hpp"

void Stage5SaSw::compute(ST4_OUT st4_input)
{
    this->old_output.th_idx = this->new_output.th_idx;
    this->old_output.th_valid = this->new_output.th_valid;
    this->old_output.dvac[0] = this->new_output.dvac[0];
    this->old_output.dvac[1] = this->new_output.dvac[1];
    this->old_output.dvbc[0] = this->new_output.dvbc[0];
    this->old_output.dvbc[1] = this->new_output.dvbc[1];
    this->old_output.dvas[0] = this->new_output.dvas[0];
    this->old_output.dvas[1] = this->new_output.dvas[1];
    this->old_output.dvas[2] = this->new_output.dvas[2];
    this->old_output.dvas[3] = this->new_output.dvas[3];
    this->old_output.dvbs[0] = this->new_output.dvbs[0];
    this->old_output.dvbs[1] = this->new_output.dvbs[1];
    this->old_output.dvbs[2] = this->new_output.dvbs[2];
    this->old_output.dvbs[3] = this->new_output.dvbs[3];

    int st4_th_idx = st4_input.th_idx;
    bool st4_th_valid = st4_input.th_valid;
    int st4_cbs = st4_input.cell_a;
    int st4_cas = st4_input.cell_b;

    if (st4_th_idx == 0 && st4_th_valid)
    {
        int a = 1;
    }

    int dvac[2] = {st4_input.dvac[0] + st4_input.dvac[1], st4_input.dvac[2] + st4_input.dvac[3]};
    int dvbc[2] = {st4_input.dvbc[0] + st4_input.dvbc[1], st4_input.dvbc[2] + st4_input.dvbc[3]};

    int dvas[N_NEIGH] = {0, 0, 0, 0};
    int dvbs[N_NEIGH] = {0, 0, 0, 0};

    for (int n = 0; n < N_NEIGH; ++n)
    {
        int i1, i2, j1, j2;

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

    this->new_output.th_idx = st4_th_idx;
    this->new_output.th_valid = st4_th_valid;
    this->new_output.dvac[0] = dvac[0];
    this->new_output.dvac[1] = dvac[1];
    this->new_output.dvbc[0] = dvbc[0];
    this->new_output.dvbc[1] = dvbc[1];
    this->new_output.dvas[0] = dvas[0];
    this->new_output.dvas[1] = dvas[1];
    this->new_output.dvas[2] = dvas[2];
    this->new_output.dvas[3] = dvas[3];
    this->new_output.dvbs[0] = dvbs[0];
    this->new_output.dvbs[1] = dvbs[1];
    this->new_output.dvbs[2] = dvbs[2];
    this->new_output.dvbs[3] = dvbs[3];
}