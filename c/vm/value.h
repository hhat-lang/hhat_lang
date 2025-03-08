#ifndef chat_value_h
#define chat_value_h

#include "common.h"

typedef double Value;


typedef struct {
    int max;
    int count;
    Value* values;
} ValueArray;


void init_value_array(ValueArray* array);
void write_value_array(ValueArray* array, Value value);
void free_value_array(ValueArray* array);
void print_value(Value value);


#endif

