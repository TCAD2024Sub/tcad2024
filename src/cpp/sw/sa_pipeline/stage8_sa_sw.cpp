#include "stage8_sa_sw.hpp"

void Stage8SaSw::compute(ST7_OUT st7_input)
{
    this->old_output.th_idx = this->new_output.th_idx;
    this->old_output.th_valid = this->new_output.th_valid;
    this->old_output.dc = this->new_output.dc;
    this->old_output.ds = this->new_output.ds;

    int st7_th_idx = st7_input.th_idx;
    bool st7_th_valid = st7_input.th_valid;
    int st7_dc = st7_input.dc;

    if (st7_th_idx == 0 && st7_th_valid)
    {
        int a = 1;
    }

    int st7_dvas = st7_input.dvas;
    int st7_dvbs = st7_input.dvbs;

    int ds = st7_dvas + st7_dvbs;

    this->new_output.th_idx = st7_th_idx;
    this->new_output.th_valid = st7_th_valid;
    this->new_output.dc = st7_dc;
    this->new_output.ds = ds;
}
