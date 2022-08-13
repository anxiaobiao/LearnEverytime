# include <stdio.h>
#include "include/drive/operation_drive.h"

int main(){
    int a, b;
    char opera;
	printf("请输入数字:");
    scanf("%c", &opera);
    printf("请输入符号:");
    scanf("%d%d", &a, &b);

    void *operation = Operation_C_new(a, b, opera);
    int res = Operation_C_res(operation);
    printf("\n结果为：%d%c%d=%d", a, opera, b, res);
	return 0;
}

