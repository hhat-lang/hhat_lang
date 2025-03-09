#include <stdio.h>
#include "common.h"
#include "compiler.h"
#include "debug.h"
#include "vm.h"


VM vm;


void reset_stack() {
    vm.stack_top = vm.stack;
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


InterpretResult run() {
#define READ_BYTE() (*vm.ip++)
#define READ_LITERAL() (vm.chunk->vals.values[READ_BYTE()])
#define BINARY_OP(op) \
    do { \
        double b = pop(); \
        double a = pop(); \
        push(a op b); \
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

            case OP_NEGATE: { push(-pop()); break; }

            case OP_ADD: { BINARY_OP(+); break;  }

            case OP_SUB: { BINARY_OP(-); break; }

            case OP_MUL: { BINARY_OP(*); break; }

            case OP_DIV: { BINARY_OP(/); break; }                

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


