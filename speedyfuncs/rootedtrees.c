#include <stdio.h>
#include <stdlib.h>

void printtree(int *tree, int len);
int *firsttree(int n);
void successortree(int *tree, int n);

void printtree(int *tree, int len)
{
    printf("[");

    for(int i = 0; i < len-1; i++) {
        printf("%d, ", tree[i]);
    }

    printf("%d]\n", tree[len-1]);
}

int *first_tree(int n)
{
    int *tree = malloc(n);
    for(int i = 0; i < n; i++){
        tree[i] = i+1;
    }
    
    return tree;
}

void next_tree(int *tree, int n) {
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

void enumerate_trees(int n, int printout)
{
    if(n < 1) {
        printf("ERROR: A tree requires at least one node.\n");
        return;
    }
    if(printout) printf("Producing rooted trees on %d nodes\n", n);

    int *tree = first_tree(n);

    if(n == 1) {
        if(printout) printtree(tree, n);
        printf("There is 1 tree on 1 node.\n");
    } else if(n == 2) {
        if(printout) printtree(tree, n);
        printf("There is 1 tree on 2 nodes.\n");
    } else {
        long count = 0;
        for(; tree[1] != tree[2]; next_tree(tree, n)) {
            if(printout) printtree(tree, n);
            count++;
        }
        count++;
        if(printout) printtree(tree, n);
        printf("There are %ld trees on %d nodes.\n", count, n);
    }
    free(tree);
    return;
}

int main(int argc, char *argv[])
{
    int n, printout;
    if(argc < 2){
        n = 0;
        printout = 0;
    } else {
        n = atoi(argv[1]);
        if (argc < 3) {
            printout = 0;
        } else {
            printout = atoi(argv[2]);
        }
    }
    enumerate_trees(n, printout);

    return 0;
}