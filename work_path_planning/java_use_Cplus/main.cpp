#include<iostream>
#include"inter.h"

int main(){
    Point point = {1,2,3};
    int arr[] = {10, 11, 12, 13};
    int len_x = 4;
    Point a = add(point, arr, len_x);
    std::cout << a.x << ' ' << a.y << ' ' << a.z << std::endl;
    return 1;
}