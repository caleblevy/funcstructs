#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

typedef struct RootedTree {
    int node_count;
    int *level_sequence;
} RootedTree;


RootedTree *first_tree(int n)
{
    RootedTree *tree = malloc(sizeof(RootedTree));
    assert(tree != NULL);

    tree->node_count = n;

    // initialize the first rooted tree at range(n)
    tree->level_sequence = malloc(n);
    for(int i = 0; i < n; i++) {
        tree->level_sequence[i] = i+1;
    }

    return tree;
}


void print_tree(RootedTree *tree)
{
    printf("[");
    for(int i = 0; i < tree->node_count-1; i++) {
        printf("%d, ", tree->level_sequence[i]);
    }
    printf("%d]\n", tree->level_sequence[tree->node_count-1]);
}


void next_tree(RootedTree *tree) 
{
    int p = tree->node_count-1;
    while(tree->level_sequence[p] == tree->level_sequence[1]) {
        p--;
    }

    int q = p-1;
    while(tree->level_sequence[q] >= tree->level_sequence[p]) {
        q--;
    }

    for(int i = p; i < tree->node_count; i++) {
        tree->level_sequence[i] = tree->level_sequence[i-(p-q)];
    }
}


void enumerate_trees(int n, int printout)
{
    if(n < 1) {
        printf("ERROR: A tree requires at least one node.\n");
        return;
    }
    if(printout) printf("Enumerating rooted trees on %d nodes\n", n);
    printf("-----------------------------------\n");

    struct RootedTree *tree = first_tree(n);

    if(n == 1) {
        if(printout) print_tree(tree);
        printf("There is 1 tree on 1 node.\n");
        return;
    } else if(n == 2) {
        if(printout) print_tree(tree);
        printf("There is 1 tree on 2 nodes.\n");
        return;
    }

    long count = 0;
    for(; tree->level_sequence[1] != tree->level_sequence[2]; next_tree(tree)) {
        if(printout) print_tree(tree);
        count++;
    }
    count++;
    if(printout) print_tree(tree);
    printf("There are %ld trees on %d nodes.\n", count, n);

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