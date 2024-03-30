
#ifndef CPP_PIPELINE_SA_HLS_H
#define CPP_PIPELINE_SA_HLS_H

#include "defines_sa_hls.hpp"

#include "stage0_sa_hls.hpp"
#include "stage1_sa_hls.hpp"
#include "stage2_sa_hls.hpp"
#include "stage3_sa_hls.hpp"
#include "stage4_sa_hls.hpp"
#include "stage5_sa_hls.hpp"
#include "stage6_sa_hls.hpp"
#include "stage7_sa_hls.hpp"
#include "stage8_sa_hls.hpp"
#include "stage9_sa_hls.hpp"

class PipelineSaHls
{
private:
public:
#ifdef ARRAY_INLINE
    static void exec_pipeline(
        ap_int<8> *n2c,
        ap_int<8> *c2n,
        ap_int<8> *n);
#else
    static void exec_pipeline(
        ap_int<8> **n2c,
        ap_int<8> **c2n,
        ap_int<8> **n);
#endif
        private:
};

#endif
