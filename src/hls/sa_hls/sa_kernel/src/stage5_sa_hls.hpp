#ifndef CPP_STAGE5_SA_HLS_H
#define CPP_STAGE5_SA_HLS_H

#include "types_sa_hls.hpp"
#include "util_sa_hls.hpp"

class Stage5SaHls
{
private:
public:
    ST5_OUT m_new_output = {0, false, {0, 0}, {0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}};
    ST5_OUT m_old_output = {0, false, {0, 0}, {0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}};

    void compute(ST4_OUT st4_input);
};
#endif