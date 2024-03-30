#include "stage6_sa_sw.hpp"

void Stage6SaSw::compute(ST5_OUT st5_input)
{
    this->old_output.th_idx = this->new_output.th_idx;
    this->old_output.th_valid = this->new_output.th_valid;
    this->old_output.dvac = this->new_output.dvac;
    this->old_output.dvbc = this->new_output.dvbc;
    this->old_output.dvas[0] = this->new_output.dvas[0];
    this->old_output.dvas[1] = this->new_output.dvas[1];
    this->old_output.dvbs[0] = this->new_output.dvbs[0];
    this->old_output.dvbs[1] = this->new_output.dvbs[1];

    int st5_th_idx = st5_input.th_idx;
    bool st5_th_valid = st5_input.th_valid;

    if (st5_th_idx == 0 && st5_th_valid)
    {
        int a = 1;
    }

    int dvac = st5_input.dvac[0] + st5_input.dvac[1];
    int dvbc = st5_input.dvbc[0] + st5_input.dvbc[1];
    int dvas[2] = {st5_input.dvas[0] + st5_input.dvas[1], st5_input.dvas[2] + st5_input.dvas[3]};
    int dvbs[2] = {st5_input.dvbs[0] + st5_input.dvbs[1], st5_input.dvbs[2] + st5_input.dvbs[3]};

    this->new_output.th_idx = st5_th_idx;
    this->new_output.th_valid = st5_th_valid;
    this->new_output.dvac = dvac;
    this->new_output.dvbc = dvbc;
    this->new_output.dvas[0] = dvas[0];
    this->new_output.dvas[1] = dvas[1];
    this->new_output.dvbs[0] = dvbs[0];
    this->new_output.dvbs[1] = dvbs[1];
}