#include "CHeterodyning.h"

extern double data [SAMPLE_COUNT];
extern double carrier[SAMPLE_COUNT];

double result [SAMPLE_COUNT];

int main(int argc, char**argv){
    printf("Running Unthreaded Test\n");
    printf("Precision sizeof %ld\n", sizeof(double));
    

    printf("Total amount of samples: %ld\n", sizeof(data) / sizeof(data[0]));
    

    tic(); // start the timer
    for (int i = 0;i<SAMPLE_COUNT;i++ ){
        result[i] = data[i] * carrier[i];
    }
    double t = toc();
    printf("Time: %lf ms\n",t/1e-3);
    printf("End Unthreaded Test\n");
    return 0;
}
