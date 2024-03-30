#ifndef DEFINES_SA_HLS_H
#define DEFINES_SA_HLS_H

#define ARRAY_INLINE
#define PRAGMAS

#define N_NEIGH 4
#define N_THREADS 6
#define N_CELLS 100
#define N_CELLS_SQRT 10
#define N_CELLS_POW 10000
#define N_LINES N_CELLS_SQRT
#define N_COLUMNS N_CELLS_SQRT
#define MESH
// #define ONE_HOP
#define EXEC_TIMES 1000
#define MAX_COUNTER (N_CELLS_POW * EXEC_TIMES)

#ifdef ARRAY_INLINE
#define N_C_N_DATA N_THREADS *N_CELLS
#define N_N_DATA N_CELLS *N_NEIGH
#endif

#endif
