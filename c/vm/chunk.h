#ifndef chat_chunk_h
#define chat_chunk_h

#include "common.h"
#include "value.h"

typedef enum {
    OP_LITERAL,
    OP_LITERAL_LONG,
    OP_NEGATE,
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_DIV,
    OP_RETURN,
} OpCode;

typedef struct {
    int count;
    int max; 
    uint8_t* code;
    ValueArray vals; 
} Chunk;

void init_chunk(Chunk* chunk);
void free_chunk(Chunk* chunk);
void write_chunk(Chunk* chunk, uint8_t byte);
int add_vals(Chunk* chunk, Value value);


#endif


