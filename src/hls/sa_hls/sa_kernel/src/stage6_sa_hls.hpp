#ifndef CPP_STAGE6_SA_HLS_H
#define CPP_STAGE6_SA_HLS_H

#include "types_sa_hls.hpp"

class Stage6SaHls
{
private:
public:
    ST6_OUT m_new_output = {0, false, 0, 0, {0, 0}, {0, 0}};
    ST6_OUT m_old_output = {0, false, 0, 0, {0, 0}, {0, 0}};

    void compute(ST5_OUT st5_input);
};
#endif