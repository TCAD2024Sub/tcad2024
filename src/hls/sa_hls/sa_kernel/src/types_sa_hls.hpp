#ifndef TYPES_SA_HLS_H
#define TYPES_SA_HLS_H

#include "ap_int.h"
#include "defines_sa_hls.hpp"

struct W
{
    ap_int<8> th_idx;
    ap_int<8> cell;
    ap_int<8> node;
};

struct ST0_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    ap_int<8> cell_a;
    ap_int<8> cell_b;
};

struct ST9_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    bool sw;
};

struct ST1_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    ap_int<8> cell_a;
    ap_int<8> cell_b;
    ap_int<8> node_a;
    ap_int<8> node_b;
    ST9_OUT sw;
    W wa;
    W wb;
};

struct ST2_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    ap_int<8> cell_a;
    ap_int<8> cell_b;
    ap_int<8> node_a;
    ap_int<8> node_b;
    ap_int<8> va[N_NEIGH];
    ap_int<8> vb[N_NEIGH];
    ST9_OUT sw;
    W wa;
    W wb;
};

struct ST3_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    ap_int<8> cell_a;
    ap_int<8> cell_b;
    ap_int<8> cva[N_NEIGH];
    ap_int<8> cvb[N_NEIGH];
    ST9_OUT sw;
    W wa;
    W wb;
};

struct ST4_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    ap_int<8> cell_a;
    ap_int<8> cell_b;
    ap_int<8> cva[N_NEIGH];
    ap_int<8> cvb[N_NEIGH];
    ap_int<8> dvac[N_NEIGH];
    ap_int<8> dvbc[N_NEIGH];
};

struct ST5_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    ap_int<8> dvac[N_NEIGH / 2];
    ap_int<8> dvbc[N_NEIGH / 2];
    ap_int<8> dvas[N_NEIGH];
    ap_int<8> dvbs[N_NEIGH];
};

struct ST6_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    ap_int<8> dvac;
    ap_int<8> dvbc;
    ap_int<8> dvas[N_NEIGH / 2];
    ap_int<8> dvbs[N_NEIGH / 2];
};

struct ST7_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    ap_int<8> dc;
    ap_int<8> dvas;
    ap_int<8> dvbs;
};

struct ST8_OUT
{
    ap_int<8> th_idx;
    bool th_valid;
    ap_int<8> dc;
    ap_int<8> ds;
};

#endif
