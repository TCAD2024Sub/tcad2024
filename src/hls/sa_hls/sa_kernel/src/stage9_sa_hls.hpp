#ifndef CPP_STAGE9_SA_HLS_H
#define CPP_STAGE9_SA_HLS_H

#include "types_sa_hls.hpp"

class Stage9SaHls
{
private:
public:
    ST9_OUT m_new_output = {0, false, false};
    ST9_OUT m_old_output = {0, false, false};

    void compute(ST8_OUT st8_input);
};
#endif