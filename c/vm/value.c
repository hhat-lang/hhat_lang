#include <stdio.h>
#include "memory.h"
#include "value.h"

void init_value_array(ValueArray* array) {
    array->values = NULL;
    array->max = 0;
    array->count = 0;
}

void write_value_array(ValueArray* array, Value value) {
    if (array->max < array->count + 1) {
        int old_max = array->max;
        array->max = GROW_MAX(old_max);
        array->values = GROW_ARRAY(Value, array->values, old_max, array->max);
    }

    array->values[array->count] = value;
    array->count++;
}

void free_value_array(ValueArray* array) {
    FREE_ARRAY(Value, array->values, array->max);
    init_value_array(array);
}


void print_value(Value value) {
    printf("%g", value);
}



