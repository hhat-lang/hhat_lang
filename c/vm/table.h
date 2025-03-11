#ifndef chat_table_h
#define chat_table_h


#include "common.h"
#include "value.h"


typedef struct {
    Elem* key;
    Value value;
} Entry;


typedef struct {
    int count;
    int max;
    Entry* entries;
} Table;



void init_table(Table* table);


#endif

