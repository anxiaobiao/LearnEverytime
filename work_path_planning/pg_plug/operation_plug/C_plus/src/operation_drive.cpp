#include "../include/drive/operation_drive.h"
#include "../include/algorithm/Operation_plus.hpp"

extern void *Operation_C_new(int a, int b, char opera){
    return new Operation(a, b, opera);
}
extern void  Operation_C_delete(void *operation){
    Operation *o = (Operation *)operation;
    delete o;
}
extern int Operation_C_res(void *operation){
    Operation *o = (Operation *)operation;
    return o->res();
}