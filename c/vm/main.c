#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "common.h"
#include "chunk.h"
#include "debug.h"
#include "vm.h"


void repl() {
    char line[1024];
    for (;;) {
        printf("> ");

        if (!fgets(line, sizeof(line), stdin)) {
            printf("\n");
            break;
        }

        interpret(line);
    }
}

char* read_file(const char* path) {
    FILE* file = fopen(path, "rb");
    
    if (file == NULL) {
        fprintf(stderr, "could not open the file \"%s\".\n", path);
        exit(77);
    }

    fseek(file, 0L, SEEK_END);
    size_t file_size = ftell(file);
    rewind(file);

    char* buffer = (char*)malloc(file_size + 1);

    if (buffer == NULL) {
        fprintf(stderr, "not enough memory to read \"%s\".\n", path);
        exit(77);
    }

    size_t bytes_read = fread(buffer, sizeof(char), file_size, file);
    
    if (bytes_read < file_size) {
        fprintf(stderr, "could not read file \"%s\".\n", path);
        exit(77);
    }

    buffer[bytes_read] = '\0';

    fclose(file);
    return buffer;
}


void run_file(const char* path) {
    char* source = read_file(path);
    InterpretResult result = interpret(source);
    free(source);

    if (result == INTERPRET_COMPILE_ERROR) exit(65);
    if (result == INTERPRET_RUNTIME_ERROR) exit(70);
}


int main(int argc, const char* argv[]) {

    init_vm();

    if (argc == 1) {
        repl();
    } else if (argc == 2) {
        run_file(argv[1]);
    } else {
        fprintf(stderr, "usage: chat [path]\n");
        exit(11);
    }

    /*
    Chunk chunk;
    init_chunk(&chunk);

    int literal = add_literal(&chunk, 3.14);
    write_chunk(&chunk, OP_LITERAL);
    write_chunk(&chunk, literal);

    literal = add_literal(&chunk, 2.1);
    write_chunk(&chunk, OP_LITERAL);
    write_chunk(&chunk, literal);
    write_chunk(&chunk, OP_ADD);

    literal = add_literal(&chunk, 10.0);
    write_chunk(&chunk, OP_LITERAL);
    write_chunk(&chunk, literal);
    write_chunk(&chunk, OP_MUL);

    write_chunk(&chunk, OP_NEGATE);

    write_chunk(&chunk, OP_RETURN);
    disassemble_chunk(&chunk, "test chunk");

    interpret(&chunk);

    free_vm();
    free_chunk(&chunk);
    */

    free_vm();
    return 0;
}


