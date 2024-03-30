#ifndef CPP_STAGE4_SA_HLS_H
#define CPP_STAGE4_SA_HLS_H

#include "types_sa_hls.hpp"
#include "util_sa_hls.hpp"

class Stage4SaHls
{
private:
public:
    ST4_OUT m_new_output = {0, false, 0, 0, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {0, 0, 0, 0}, {0, 0, 0, 0}};
    ST4_OUT m_old_output = {0, false, 0, 0, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {0, 0, 0, 0}, {0, 0, 0, 0}};

    void compute(ST3_OUT st3_input);
};
#endif