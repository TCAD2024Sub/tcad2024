#include "stage0_sa_sw.hpp"

void Stage0SaSw::compute()
{
    int th_idx_c = this->th_idx;

    this->old_output.th_idx = this->new_output.th_idx;
    this->old_output.th_valid = this->new_output.th_valid;
    this->old_output.cell_a = this->new_output.cell_a;
    this->old_output.cell_b = this->new_output.cell_b;

    if (!this->th_valid[th_idx_c])
    {
        if (this->cell_a[th_idx_c] == N_CELLS - 1)
        {
            this->cell_a[th_idx_c] = 0;
            if (this->cell_b[th_idx_c] == N_CELLS - 1)
            {
                this->cell_b[th_idx_c] = 0;
            }
            else
            {
                this->cell_b[th_idx_c] += 1;
            }
        }
        else
        {
            this->cell_a[th_idx_c] += 1;
        }

        this->th_idx += 1;
        if (this->th_idx == N_THREADS)
        {
            this->th_idx = 0;
        }
    }
    this->th_valid[th_idx_c] = !this->th_valid[th_idx_c];

    th_idx_c = this->th_idx;
    this->new_output.th_idx = this->th_idx;
    this->new_output.th_valid = this->th_valid[th_idx_c];
    this->new_output.cell_a = this->cell_a[th_idx_c];
    this->new_output.cell_b = this->cell_b[th_idx_c];

    if (this->th_valid[th_idx_c] && this->th_idx == 0)
    {
        this->exec_counter += 1;
    }
}
