#ifndef CPP_STAGE5_SA_SW_H
#define CPP_STAGE5_SA_SW_H

#include "types_sa_sw.hpp"
#include "util_sa_sw.hpp"

class Stage5SaSw
{
private:
public:
    ST5_OUT new_output = {0, false, {0, 0}, {0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}};
    ST5_OUT old_output = {0, false, {0, 0}, {0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}};

    void compute(ST4_OUT st4_input);
};
#endif