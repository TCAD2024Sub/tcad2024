#ifndef CPP_STAGE4_SA_SW_H
#define CPP_STAGE4_SA_SW_H

#include "types_sa_sw.hpp"
#include "util_sa_sw.hpp"

class Stage4SaSw
{
private:
public:
    ST4_OUT new_output = {0, false, 0, 0, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {0, 0, 0, 0}, {0, 0, 0, 0}};
    ST4_OUT old_output = {0, false, 0, 0, {-1, -1, -1, -1}, {-1, -1, -1, -1}, {0, 0, 0, 0}, {0, 0, 0, 0}};

    void compute(ST3_OUT st3_input);
};
#endif