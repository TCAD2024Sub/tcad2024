
#ifndef CPP_PIPELINE_SA_SW_H
#define CPP_PIPELINE_SA_SW_H

#include "defines_sa_sw.hpp"

#include "stage0_sa_sw.hpp"
#include "stage1_sa_sw.hpp"
#include "stage2_sa_sw.hpp"
#include "stage3_sa_sw.hpp"
#include "stage4_sa_sw.hpp"
#include "stage5_sa_sw.hpp"
#include "stage6_sa_sw.hpp"
#include "stage7_sa_sw.hpp"
#include "stage8_sa_sw.hpp"
#include "stage9_sa_sw.hpp"

class PipelineSaSw
{
private:
public:
    void run_single(int (&n2c)[N_COPIES][N_THREADS][N_CELLS], int (&c2n)[N_COPIES][N_THREADS][N_CELLS],
                    int (&n)[N_CELLS][N_NEIGH]);

private:
    static void exec_pipeline(int (&n2c)[N_THREADS][N_CELLS], int (&c2n)[N_THREADS][N_CELLS], int (&n)[N_CELLS][N_NEIGH]);
};

#endif
