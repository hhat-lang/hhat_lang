#include <stdlib.h>
#include <stdio.h>
#include "debug.h"
#include "value.h"



void disassemble_chunk(Chunk* chunk, const char* name) {
    printf("== %s ==\n", name);

    for (int offset = 0; offset < chunk->count;) {
        offset = disassemble_instr(chunk, offset);
    }
}


int literal_instrr(const char* name, Chunk* chunk, int offset) {
    uint8_t vals = chunk->code[offset + 1];
    printf("%-16s %4d '", name, vals);
    print_value(chunk->vals.values[vals]);
    printf("'\n");
    return offset + 2;
}


int simple_instr(const char* name, int offset) {
    printf("%s\n", name);
    return offset + 1;
}


int disassemble_instr(Chunk* chunk, int offset) {
    printf("%04d ", offset);

    if (offset > 0 && chunk->lines[offset] == chunks->lines[offset - 1]) {
        printf("   | ");
    } else {
        printf("%4d ", chunk->lines[offset]);
    }

    uint8_t instr = chunk->code[offset];
    switch (instr) {
        case OP_LITERAL:
            return literal_instr("OP_LITERAL", chunk, offset);

        case OP_LITERAL_LONG:
            // TODO: implement it
            return -1;

        case OP_NEGATE:
            return simple_instr("OP_NEGATE", offset);

        case OP_ADD:
            return simple_instr("OP_ADD", offset);

        case OP_SUB:
            return simple_instr("OP_SUB", offset);

        case OP_MUL:
            return simple_instr("OP_MUL", offset);

        case OP_DIV:
            return simple_instr("OP_DIV", offset);    

        case OP_RETURN:
            return simple_instr("OP_RETURN", offset);

        default:
            printf("not implemented opcode %d\n", instr);
            return offset + 1;
    }
}


