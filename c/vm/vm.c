#include <stdarg.h>
#include <stdio.h>
#include "common.h"
#include "compiler.h"
#include "debug.h"
#include "value.h"
#include "vm.h"


VM vm;


void reset_stack() {
    vm.stack_top = vm.stack;
}


static void runtime_error(const char* format, ...) {
    va_list args;
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputs("\n", stderr);

    size_t instr = vm.ip - vm.chunk->code - 1;
    int line = vm.chunk->lines[instr];
    fprintf(stderr, "[line %d] in script\n", line);
    reset_stack();
}


void init_vm() {
    reset_stack();
    
}


void free_vm() {
}


void push(Value value) {
    *vm.stack_top = value;
    vm.stack_top++;
}


Value pop() {
    vm.stack_top--;
    return *vm.stack_top;
}


static Value peek(int distance) {
    return vm.stack[-1 - distance];
}


InterpretResult run() {
#define READ_BYTE() (*vm.ip++)
#define READ_LITERAL() (vm.chunk->literal.values[READ_BYTE()])
#define BINARY_OP(valueType, op) \
    do { \
      if (!IS_NUMBER(peek(0)) || !IS_NUMBER(peek(1))) { \
        runtime_error("Operands must be numbers."); \
        return INTERPRET_RUNTIME_ERROR; \
      } \
      double b = AS_NUMBER(pop()); \
      double a = AS_NUMBER(pop()); \
      push(valueType(a op b)); \
    } while (false)

    for (;;) {
#ifdef DEBUG_TRACE_EXECUTION
        printf("          ");
        for (Value* slot = vm.stack; slot < vm.stack_top; slot++) {
            printf("[ ");
            print_value(*slot);
            printf(" ]");
        }
        printf("\n");
        disassemble_instr(vm.chunk, (int)(vm.ip - vm.chunk->code));
#endif

        uint8_t instr;
        switch (instr = READ_BYTE()) {
            case OP_LITERAL: {
                Value literal = READ_LITERAL();
                push(literal);
                break;
            }

            case OP_NULL: { push(NULL_VAL); break; }

            case OP_FALSE: { push(BOOL_VAL(false)); break; }
           
            case OP_TRUE: { push(BOOL_VAL(true)); break; }

            case OP_ADD: { BINARY_OP(NUMBER_VAL, +); break;  }

            case OP_SUB: { BINARY_OP(NUMBER_VAL, -); break; }

            case OP_MUL: { BINARY_OP(NUMBER_VAL, *); break; }

            case OP_DIV: { BINARY_OP(NUMBER_VAL, /); break; }                

            case OP_RETURN: {
                print_value(pop());
                printf("\n");
                return INTERPRET_OK;
            }

        }
    }

#undef READ_LITERAL
#undef BINARY_OP
#undef READ_BYTE
}


/*
InterpretResult interpret(Chunk* chunk) {
    vm.chunk = chunk;
    vm.ip = vm.chunk->code;
    return run();
}
*/

InterpretResult interpret(const char* source) {
    Chunk chunk;
    init_chunk(&chunk);

    if (!compile(source, &chunk)) {
        free_chunk(&chunk);
        return INTERPRET_COMPILE_ERROR;
    }

    vm.chunk = &chunk;
    vm.ip = vm.chunk->code;

    InterpretResult result = run();

    free_chunk(&chunk);
    return result;

}


