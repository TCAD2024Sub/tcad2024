#ifndef CPP_UTIL_SA_SW_H
#define CPP_UTIL_SA_SW_H

#include <cmath>

void get_line_column_from_cell(int cell, int n_lines, int n_columns, int &line, int &column);

int dist_manhattan(int ia, int ja, int ib, int jb);

int dist_one_hop(int ia, int ja, int ib, int jb);

#endif
