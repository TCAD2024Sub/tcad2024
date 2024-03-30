#ifndef CPP_STAGE9_SA_SW_H
#define CPP_STAGE9_SA_SW_H

#include "types_sa_sw.hpp"

class Stage9SaSw
{
private:
public:
    ST9_OUT new_output = {0, false, false};
    ST9_OUT old_output = {0, false, false};

    void compute(ST8_OUT st8_input);
};
#endif