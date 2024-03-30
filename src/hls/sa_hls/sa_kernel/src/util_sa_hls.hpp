#ifndef CPP_UTIL_SA_HLS_H
#define CPP_UTIL_SA_HLS_H

#include <cmath>
#include "defines_sa_hls.hpp"
#include "ap_int.h"

void get_line_column_from_cell(ap_int<8> cell, ap_int<8> n_lines, ap_int<8> n_columns, ap_int<8> &line, ap_int<8> &column);

ap_int<8> dist_manhattan(ap_int<8> ia, ap_int<8> ja, ap_int<8> ib, ap_int<8> jb);

ap_int<8> dist_one_hop(ap_int<8> ia, ap_int<8> ja, ap_int<8> ib, ap_int<8> jb);

#endif
