#ifndef CPP_STAGE6_SA_SW_H
#define CPP_STAGE6_SA_SW_H

#include "types_sa_sw.hpp"

class Stage6SaSw
{
private:
public:
    ST6_OUT new_output = {0, false, 0, 0, {0, 0}, {0, 0}};
    ST6_OUT old_output = {0, false, 0, 0, {0, 0}, {0, 0}};

    void compute(ST5_OUT st5_input);
};
#endif