#ifndef chat_debug_h
#define chat_debug h

#include "chunk.h"


void disassemble_chunk(Chunk* chunk, const char* name);
int disassemble_instr(Chunk* chunk, int offset);


#endif

