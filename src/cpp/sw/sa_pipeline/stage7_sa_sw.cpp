#include "stage7_sa_sw.hpp"

void Stage7SaSw::compute(ST6_OUT st6_input)
{
    this->old_output.th_idx = this->new_output.th_idx;
    this->old_output.th_valid = this->new_output.th_valid;
    this->old_output.dc = this->new_output.dc;
    this->old_output.dvas = this->new_output.dvas;
    this->old_output.dvbs = this->new_output.dvbs;

    int st6_th_idx = st6_input.th_idx;
    bool st6_th_valid = st6_input.th_valid;
    int st6_dvac = st6_input.dvac;
    int st6_dvbc = st6_input.dvbc;

    if (st6_th_idx == 0 && st6_th_valid)
    {
        int a = 1;
    }

    int dc = st6_dvac + st6_dvbc;
    int dvas = st6_input.dvas[0] + st6_input.dvas[1];
    int dvbs = st6_input.dvbs[0] + st6_input.dvbs[1];

    this->new_output.th_idx = st6_th_idx;
    this->new_output.th_valid = st6_th_valid;
    this->new_output.dc = dc;
    this->new_output.dvas = dvas;
    this->new_output.dvbs = dvbs;
}