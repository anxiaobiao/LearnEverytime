#include <stdio.h>
#include <stdlib.h>

int operation_C(int* a,int len);
int operation_C(int* a,int len){

    // return a+b;
    // if(opera == '+'){
    //     return a + b;
    // }else if (opera == '-'){
    //     return a - b;
    // }else{
    //     exit(EXIT_FAILURE);
    // }
    int res = 0;
    for(int i = 0; i < len; i++){
        res += a[i];
    }
    return res;
    
}

void main(){
    // char opera;
    // int a, b;
    int res;

    // printf("111");
    // scanf("%c", &opera);
    // printf("\n222");
    // scanf("%d%d", &a, &b);

    int a[] = {1,2,3,4,5};
    res = operation_C(a,sizeof(a)/sizeof(a[0]));
    
    printf("%d\n",res);

}