#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

struct FixedLengthPartition {
    int n; // size of the partition
    int L; // length of the partition
    int *components; // The partition itself.
};

void print_partition(struct FixedLengthPartition *partition)
{
    printf("[");
    for(int i = 0; i < partition->L-1; i++) {
        printf("%d, ", partition->components[i]);
    }
    printf("%d]\n", partition->components[partition->L-1]);
}


void set_minimal_partition(/*struct FixedLenthPartition *partition*/ int n, int L)
{
    int binsize = n / L;
    int overstuffed = n - L*binsize;
    int regular = L - overstuffed;
    int ones_count = (binsize != 1) ? 1 : regular + 1;
    printf("%d\n", ones_count);
}

int main(int argc, char *argv[])
{
    set_minimal_partition(4, 1);
    set_minimal_partition(20, 4);
    set_minimal_partition(20, 20);
}