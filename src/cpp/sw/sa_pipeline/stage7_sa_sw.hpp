#ifndef CPP_STAGE7_SA_SW_H
#define CPP_STAGE7_SA_SW_H

#include "types_sa_sw.hpp"

class Stage7SaSw
{
private:
public:
    ST7_OUT new_output = {0, false, 0, 0, 0};
    ST7_OUT old_output = {0, false, 0, 0, 0};

    void compute(ST6_OUT st6_input);
};
#endif