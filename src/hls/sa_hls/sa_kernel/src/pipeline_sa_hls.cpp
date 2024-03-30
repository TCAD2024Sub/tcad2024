#include "pipeline_sa_hls.hpp"

#ifdef ARRAY_INLINE
void PipelineSaHls::exec_pipeline(
    ap_int<8> *n2c,
    ap_int<8> *c2n,
    ap_int<8> *n)
#else
void PipelineSaHls::exec_pipeline(
    ap_int<8> **n2c,
    ap_int<8> **c2n,
    ap_int<8> **n)
#endif
{

    Stage0SaHls st0;
    Stage1SaHls st1;
    Stage2SaHls st2;
    Stage3SaHls st3;
    Stage4SaHls st4;
    Stage5SaHls st5;
    Stage6SaHls st6;
    Stage7SaHls st7;
    Stage8SaHls st8;
    Stage9SaHls st9;

    for (long counter = 0; counter < MAX_COUNTER; counter++)
    {
#ifdef PRAGMAS
#pragma HLS PIPELINE II = 1 style = frp
#endif
        st0.compute();
        st1.compute(st0.m_old_output, st9.m_old_output, st1.m_old_output.wb, c2n);
        st2.compute(st1.m_old_output, n);
        st3.compute(st2.m_old_output, st3.m_old_output.wb, n2c);
        st4.compute(st3.m_old_output);
        st5.compute(st4.m_old_output);
        st6.compute(st5.m_old_output);
        st7.compute(st6.m_old_output);
        st8.compute(st7.m_old_output);
        st9.compute(st8.m_old_output);
    }
}
