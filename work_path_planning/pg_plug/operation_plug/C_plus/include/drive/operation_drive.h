#ifndef Operation_C_H
#define Operation_C_H

// //  use int_t
// #ifdef __cplusplus
// #   include <cstddef>
// #   include <cstdint>
// #else
// #   include <stddef.h>
// #   include <stdint.h>
// #endif

#ifdef __cplusplus
extern "C" {
#endif
 
    extern void *Operation_C_new(int a, int b, char opera);
    extern void  Operation_C_delete(void *operation);
    extern int Operation_C_res(void *operation);
 
#ifdef __cplusplus
}
#endif
 
#endif Operation_C_H