#include <stdio.h>
#include <stdlib.h>

void addone(int *t, int len)
{
    for(int i = 0; i < len; i++){
        t[i] += 1;
    }
}

int main(int argc, char *argv[])
{
    int n;
    if(argc < 2){
        n = 0;
    } else {
        n = atoi(argv[1]);
    }
    printf("Producing rooted trees on %d nodes\n", n);

    int tree[n];
    for(int i = 0; i < n; i++){
        tree[i] = i+1;
    }
    addone(tree, n);
    for(int i = 0; i < n; i++){
        printf("tree[%d]: %d\n", i, tree[i]);
    }
}