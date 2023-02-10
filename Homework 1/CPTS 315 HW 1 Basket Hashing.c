//(C) Andrew Balaschak, 2023
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
