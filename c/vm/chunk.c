#include <stdlib.h>
#include <stdio.h>
#include "chunk.h"
#include "memory.h"

void init_chunk(Chunk* chunk) {
    chunk->count = 0;
    chunk->max = 0;
    chunk->code = NULL;
    init_value_array(&chunk->vals);
}

void free_chunk(Chunk* chunk) {
    FREE_ARRAY(uint8_t, chunk->code, chunk->max);
    free_value_array(&chunk->vals);
    init_chunk(chunk);
}

void write_chunk(Chunk* chunk, uint8_t byte) {
    if (chunk->max < chunk->count + 1) {
        int old_max = chunk->max;
        chunk->max = GROW_MAX(old_max);
        chunk->code = GROW_ARRAY(uint8_t, chunk->code, old_max, chunk->max);
    }

    chunk->code[chunk->count] = byte;
    chunk->count++;
}

int add_vals(Chunk* chunk, Value value) {
    write_value_array(&chunk->vals, value);
    return chunk->vals.count - 1;
}




