#include "util_sa_sw.hpp"

void get_line_column_from_cell(int cell, int n_lines, int n_columns, int &line, int &column)
{
    line = cell / n_lines;
    column = cell % n_columns;
}

int dist_manhattan(int ia, int ja, int ib, int jb)
{
    return abs(ia - ib) + abs(ja - jb);
}

int dist_one_hop(int ia, int ja, int ib, int jb)
{
    int i = abs(ia - ib);
    int j = abs(ja - jb);
    return (int)ceil(i / 2.0) + (int)ceil(j / 2.0);
}