
#include "saTop.hpp"

extern "C" void simulatedAnnealingTop(ap_int<8> *n2c, ap_int<8> *c2n, ap_int<8> *n)
{
#ifdef PRAGMAS
#pragma HLS INTERFACE m_axi port = n2c offset = slave
#pragma HLS INTERFACE m_axi port = c2n offset = slave
#pragma HLS INTERFACE m_axi port = n offset = slave
#pragma HLS INTERFACE s_axilite port = return
#endif

#ifdef ARRAY_INLINE
    ap_int<8> n2c_l[N_C_N_DATA];
    ap_int<8> c2n_l[N_C_N_DATA];
    ap_int<8> n_l[N_N_DATA];

#ifdef PRAGMAS
#pragma hls ARRAY_RESHAPE variable = n2c_l type = block factor = N_CELLS
#pragma hls ARRAY_RESHAPE variable = c2n_l type = block factor = N_CELLS
#pragma hls ARRAY_RESHAPE variable = n_l type = block factor = N_NEIGH
#endif

    memcpy((ap_int<8> *)n2c_l, n2c, N_C_N_DATA * sizeof(ap_int<8>));
    memcpy((ap_int<8> *)c2n_l, c2n, N_C_N_DATA * sizeof(ap_int<8>));
    memcpy((ap_int<8> *)n_l, n, N_N_DATA * sizeof(ap_int<8>));

    static PipelineSaHls sa_pipeline_hw;
    sa_pipeline_hw.exec_pipeline((ap_int<8> *)n2c_l, (ap_int<8> *)c2n_l, (ap_int<8> *)n_l);

    memcpy(c2n, (ap_int<8> *)c2n_l, N_C_N_DATA * sizeof(ap_int<8>));
#else
    ap_int<8> n2c_l[N_THREADS][N_CELLS];
    ap_int<8> c2n_l[N_THREADS][N_CELLS];
    ap_int<8> n_l[N_CELLS][N_NEIGH];

    for (ap_int<8> i = 0; i < N_THREADS; i++)
    {
        for (ap_int<8> j = 0; j < N_CELLS; j++)
        {
            ap_int<8> idx = i * N_THREADS + j;
            n2c_l[i][j] = n2c[idx];
            c2n_l[i][j] = c2n[idx];
        }
    }
    for (ap_int<8> i = 0; i < N_CELLS; i++)
    {
        for (ap_int<8> j = 0; j < N_NEIGH; j++)
        {
            ap_int<8> idx = i * N_CELLS + j;
            n_l[i][j] = n[idx];
        }
    }

    static PipelineSaHls sa_pipeline_hw;
    sa_pipeline_hw.exec_pipeline((ap_int<8> **)n2c_l, c2n_l, (ap_int<8> **)n_l);

    for (ap_int<8> i = 0; i < N_THREADS; i++)
    {
        for (ap_int<8> j = 0; j < N_CELLS; j++)
        {
            ap_int<8> idx = i * N_THREADS + j;
            c2n[idx] = c2n_l[i][j];
        }
    }
#endif
}
