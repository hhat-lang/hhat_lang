#ifndef chat_chunk_h
#define chat_chunk_h

#include "common.h"
#include "value.h"

typedef enum {
    // classical
    OP_LITERAL,
    OP_LITERAL_LONG,
    OP_NULL,
    OP_TRUE,
    OP_FALSE,
    OP_NEGATE,
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_DIV,
    OP_RETURN,
    //quantum
    OP_QTRUE,
    OP_QFALSE,
 
} OpCode;


typedef struct {
    int count;
    int max; 
    uint8_t* code;
    int* lines;
    ValueArray literal; 
} Chunk;


void init_chunk(Chunk* chunk);
void free_chunk(Chunk* chunk);
void write_chunk(Chunk* chunk, uint8_t byte, int line);
int add_literal(Chunk* chunk, Value value);


#endif


