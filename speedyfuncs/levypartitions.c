#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

typedef struct FixedLengthPartition {
    int n; // size of the partition
    int L; // length of the partition
    int ones; // number of "ones" in the partition (plus 1)
    int *comps; // components of the partition.
} FixedLengthPartition;

void print_partition(FixedLengthPartition *part)
{
    printf("[");
    for(int i = 0; i < part->L-1; i++) {
        printf("%d, ", part->comps[i]);
    }
    printf("%d]\n", part->comps[part->L-1]);
}

/* 
 * Set the tail end of partition *part to the minimal partition of length n and
 * size L.
 */
void minimize_partition_tail(FixedLengthPartition *part, int n, int L)
{
    int binsize = n / L;
    int overstuffed = n - L*binsize;
    int regular = L - overstuffed;
    
    part->ones = (binsize != 1) ? 1 : regular + 1;
    for(int i = part->L - L; i < part->L - L + overstuffed; i++){
        part->comps[i] += binsize+1;
    }
    for(int i = part->L - L + overstuffed; i < part->L; i++) {
        part->comps[i] += binsize;
    }
}

FixedLengthPartition *first_partition(int n, int L)
{
    FixedLengthPartition *part = malloc(sizeof(FixedLengthPartition));
    assert(part != NULL);
    
    part->n = n;
    part->L = L;
    part->ones = 1;
    part->comps = malloc(L);
    for(int i = 0; i < L; i++) {
        part->comps[i] = 0;
    }
    minimize_partition_tail(part, n, L);
    return part;
}

void enumerate_fixed_lex_partitions(int n, int L)
{
    if(!L) {
        if(!n) {
            printf("[]\n");
            printf("There is 1 partition of n=0 into L=0 parts.\n");
        } else {
            printf("There are 0 partitions of n=%d into L=0 parts.\n", n);
        }
        return;

    } else if(L == 1) {
        if(n > 0) {
            printf("[%d]\n", n);
            printf("There is 1 partition of n=%d into L=1 part.\n", n);
        } else {
            printf("There are 0 partitions of n=0 into L=1 part.\n");
        }
        return;
    } else if(n < L) {
        printf("There are 0 partitions of n=%d into L=%d parts.\n", n, L);
    }
}

int main(int argc, char *argv[])
{
    print_partition(first_partition(10, 4));
    enumerate_fixed_lex_partitions(0,4);
}