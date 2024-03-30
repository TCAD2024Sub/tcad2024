#ifndef CPP_STAGE7_SA_HLS_H
#define CPP_STAGE7_SA_HLS_H

#include "types_sa_hls.hpp"

class Stage7SaHls
{
private:
public:
    ST7_OUT m_new_output = {0, false, 0, 0, 0};
    ST7_OUT m_old_output = {0, false, 0, 0, 0};

    void compute(ST6_OUT st6_input);
};
#endif