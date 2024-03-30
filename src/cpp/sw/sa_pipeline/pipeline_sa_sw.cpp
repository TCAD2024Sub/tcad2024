#include "pipeline_sa_sw.hpp"

void PipelineSaSw::run_single(int (&n2c)[N_COPIES][N_THREADS][N_CELLS], int (&c2n)[N_COPIES][N_THREADS][N_CELLS],
                               int (&n)[N_CELLS][N_NEIGH])
{

    for (int i = 0; i < N_COPIES; ++i)
    {
        exec_pipeline(n2c[i], c2n[i], n);
    }
}

void PipelineSaSw::exec_pipeline(int (&n2c)[N_THREADS][N_CELLS], int (&c2n)[N_THREADS][N_CELLS], int (&n)[N_CELLS][N_NEIGH])
{

    Stage0SaSw st0 = Stage0SaSw();
    Stage1SaSw st1 = Stage1SaSw();
    Stage2SaSw st2 = Stage2SaSw();
    Stage3SaSw st3 = Stage3SaSw();
    Stage4SaSw st4 = Stage4SaSw();
    Stage5SaSw st5 = Stage5SaSw();
    Stage6SaSw st6 = Stage6SaSw();
    Stage7SaSw st7 = Stage7SaSw();
    Stage8SaSw st8 = Stage8SaSw();
    Stage9SaSw st9 = Stage9SaSw();

    for (long counter = 0; counter < MAX_COUNTER; counter++)
    {
        st0.compute();
        st1.compute(st0.old_output, st9.old_output, st1.old_output.wb, c2n);
        st2.compute(st1.old_output, n);
        st3.compute(st2.old_output, st3.old_output.wb, n2c);
        st4.compute(st3.old_output);
        st5.compute(st4.old_output);
        st6.compute(st5.old_output);
        st7.compute(st6.old_output);
        st8.compute(st7.old_output);
        st9.compute(st8.old_output);
    }
}
