//Code (c) Andrew Balaschak, 2023

/*
This question is about the PCY algorithm for counting frequent pairs of items. Suppose we have six items numbered 1, 2, 3, 4, 5, 6. Consider the following twelve baskets.
    1.  {1,2,3}
    2.  {2,3,4}
    3.  {3,4,5}
    4.  {4,5,6}
    5.  {1,3,5}
    6.  {2,4,6}
    7.  {1,3,4}
    8.  {2,4,5}
    9.  {3,5,6}
    10. {1,2,4}
    11. {2,3,5}
    12. {3,4,6}
    
Suppose the support threshold is 4. On the first pass of the PCY algorithm, we use a hash table with 11 buckets, and the set {i,j} is hashed to i × j mod 11.
    a) By any method, compute the support for each item and each pair of items.
    b) Which pairs hash to which buckets?
    c) Which buckets are frequent?
    d) Which pairs are counted on the second pass of the PCY algorithm?
*/

#include <stdio.h>

int main(){
    int baskets[12][3] = {{1,2,3}, {2,3,4}, {3,4,5}, {4,5,6}, {1,3,5},
        {2,4,6}, {1,3,4}, {2,4,5}, {3,5,6}, {1,2,4}, {2,3,5}, {3,4,6}};
    
    int table[11];
    
    //hash each pair from the baskets
    for(int i = 0; i < 12; i++){
        for(int j = 0; j < 3; j++){
            int hash = (baskets[i][j] * baskets[i][(j+1)%3]) % 11;
            table[hash]++;

            printf("{%d,%d} : ", baskets[i][j], baskets[i][(j+1)%3]);
            printf("%d", hash);
            printf("\n");
            
        }
    }
    
    printf("\n");
    
    //print hash table
    for(int i = 0; i < 11; i++){
        printf("%d : %d", i, table[i]);
        printf("\n");
    }

    return 0;
}
