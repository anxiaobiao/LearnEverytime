#include<iostream>
#include"inter.h"

Point add(Point point, int arr[], int len_x){
    point.x += 1;
    point.y += 1;
    point.z += 1;
    return point;

}

#ifdef __cplusplus
extern "C"{
#endif

    Point* jna_add(Point point, int arr[], int len_x){
        Point a = add(point, arr, len_x);
        Point *ans = new Point[1];
        for(int i = 0; i < 1; ++i){
            ans[i].x = a.x;
            ans[i].y = a.y;
            ans[i].z = a.z;
        }

        for(int i = 0; i < len_x; ++i){
            printf("input【%d】",arr[i]);
        }

        return ans;


    }

#ifdef __cplusplus
}
#endif