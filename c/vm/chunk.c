#include <stdlib.h>
#include <stdio.h>
#include "chunk.h"
#include "memory.h"

void init_chunk(Chunk* chunk) {
    chunk->count = 0;
    chunk->max = 0;
    chunk->code = NULL;
    chunk->lines = NULL;
    init_value_array(&chunk->literal);
}

void free_chunk(Chunk* chunk) {
    FREE_ARRAY(uint8_t, chunk->code, chunk->max);
    FREE_ARRAY(int, chunk->lines, chunk->max);
    free_value_array(&chunk->literal);
    init_chunk(chunk);
}

void write_chunk(Chunk* chunk, uint8_t byte, int line) {
    if (chunk->max < chunk->count + 1) {
        int old_max = chunk->max;
        chunk->max = GROW_MAX(old_max);
        chunk->code = GROW_ARRAY(uint8_t, chunk->code, old_max, chunk->max);
        chunk->lines = GROW_ARRAY(int, chunk->lines, old_max, chunk->max);
    }

    chunk->code[chunk->count] = byte;
    chunk->lines[chunk->count] = line;
    chunk->count++;
}

int add_literal(Chunk* chunk, Value value) {
    write_value_array(&chunk->literal, value);
    return chunk->literal.count - 1;
}




