#include <stdio.h>
#include "sa_pipeline_sw.cpp"

int main(int argc, char *argv[]) {
    int c2n[N_COPIES][N_THREADS][N_CELLS];
    int n2c[N_COPIES][N_THREADS][N_CELLS];
    int n[N_CELLS][N_NEIGH];

    for (int i = 0; i < N_COPIES; i++) {
        for (int j = 0; j < N_THREADS; j++) {
            for (int k = 0; k < N_CELLS; k++) {
                c2n[i][j][k] = -1;
                n2c[i][j][k] = -1;
            }
        }
    }

    for (auto &i: n) {
        for (int &j: i) {
            j = -1;
        }
    }

    //Neighborhood for test
    n[0][0] = 2;
    n[0][1] = 1;
    n[0][2] = 9;
    n[1][0] = 0;
    n[2][0] = 0;
    n[2][1] = 6;
    n[3][0] = 5;
    n[3][1] = 4;
    n[3][2] = 9;
    n[4][0] = 3;
    n[5][0] = 3;
    n[5][1] = 6;
    n[6][0] = 2;
    n[6][1] = 5;
    n[6][2] = 7;
    n[7][0] = 6;
    n[7][1] = 8;
    n[8][0] = 7;
    n[9][0] = 0;
    n[9][1] = 3;
    n[9][2] = 10;
    n[10][0] = 9;

    //c2n for tests
    c2n[0][0][0] = 0;
    c2n[0][0][1] = 1;
    c2n[0][0][2] = 2;
    c2n[0][0][3] = 3;
    c2n[0][0][4] = 4;
    c2n[0][0][5] = 5;
    c2n[0][0][6] = 6;
    c2n[0][0][7] = 7;
    c2n[0][0][8] = 8;
    c2n[0][0][9] = 9;
    c2n[0][0][10] = 10;

    //n2c for tests
    n2c[0][0][0] = 0;
    n2c[0][0][1] = 1;
    n2c[0][0][2] = 2;
    n2c[0][0][3] = 3;
    n2c[0][0][4] = 4;
    n2c[0][0][5] = 5;
    n2c[0][0][6] = 6;
    n2c[0][0][7] = 7;
    n2c[0][0][8] = 8;
    n2c[0][0][9] = 9;
    n2c[0][0][10] = 10;

    //printf("%d ", c2n[0][0][0]);

    SAPipelineSw sa_pipeline_sw = *new SAPipelineSw();
    sa_pipeline_sw.run_single(n2c, c2n, n);

    return 0;
}