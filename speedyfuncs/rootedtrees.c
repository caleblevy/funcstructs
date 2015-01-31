#include <stdio.h>
#include <stdlib.h>

void printtree(int *tree, int len);
void successortree(int *tree, int n);

void printtree(int *tree, int len)
{
    printf("[");

    for(int i = 0; i < len-1; i++) {
        printf("%d, ", tree[i]);
    }

    printf("%d]\n", tree[len-1]);
}

void successortree(int *tree, int n) {
    int p = n-1;
    while(tree[p] == tree[1]) {
        p--;
    }
    int q = p-1;
    while(tree[q] >= tree[p]) {
        q--;
    }
    for(int i = p; i < n; i++) {
        tree[i] = tree[i-(p-q)];
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
    if(n < 1) {
        printf("ERROR: A tree requires at least one node.\n");
        return 1;
    }
    printf("Producing rooted trees on %d nodes\n", n);

    int tree[n];
    for(int i = 0; i < n; i++){
        tree[i] = i+1;
    }

    if(n == 1) {
        printtree(tree, n);
        printf("There is 1 tree on 1 node.\n");
        return 0;
    } else if(n == 2) {
        printtree(tree, n);
        printf("There is 1 tree on 2 nodes.\n");
        return 0;
    }
    long count = 1;
    printtree(tree, n);
    while(tree[1] != tree[2]) {
        successortree(tree, n);
        printtree(tree, n);
        count++;
    }
    printf("There are %ld trees on %d nodes.\n", count, n);
    return 0;
}