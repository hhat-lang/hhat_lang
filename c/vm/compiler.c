#include <stdio.h>
#include <stdlib.h>
#include "common.h"
#include "compiler.h"
#include "scanner.h"


#ifdef DEBUG_PRINT_CODE
#include "debug.h"
#endif


typedef struct {
    Token current;
    Token previous;
    bool had_error;
    bool panic_mode;
} Parser;


typedef void (*ParseFn)();


typedef enum {
    PREC_NONE,
    PREC_ASSIGNMENT,
    PREC_CALL,
    PREC_PRIMARY,
} Precedence;


typedef struct {
    ParseFn prefix;
    ParseFn infix;
    Precedence precedence;
} ParseRule;


Parser parser;
Chunk* compiling_chunk;


static Chunk* current_chunk() {
    return compiling_chunk;
}


static void error_at(Token* token, const char* message) {
    if (parser.panic_mode) return;
    parser.panic_mode = true;
    fprintf(stderr, "[line %d] Error", token->line);

    if (token->line == TOKEN_EOF) {
        fprintf(stderr, " at end");
    } else if (token->type == TOKEN_ERROR) {
        // nothing (?)
    } else {
        fprintf(stderr, " at '%.*s'", token->length, token->start);
    }

    fprintf(stderr, ": %s\n", message);
    parser.had_error = true;
}


static void error(const char* message) {
    error_at(&parser.previous, message);
}


static void error_at_current(const char* message) {
    error_at(&parser.previous, message);
}


static void advance() {
    parser.previous = parser.current;

    for (;;) {
        parser.current = scan_token();
        if (parser.current.type != TOKEN_ERROR) break;

        error_at_current(parser.current.start);
    }
}


static void consume(TokenType type, const char* message) {
    if (parser.current.type == type) {
        advance();
        return;
    }

    error_at_current(message);
}


static void emit_byte(uint8_t byte) {
    write_chunk(current_chunk(), byte, parser.previous.line);
}


static void emit_bytes(uint8_t byte1, uint8_t byte2) {
    emit_byte(byte1);
    emit_byte(byte2);
}


static void emit_return() {
    emit_byte(OP_RETURN);
}


static void expression();
static ParseRule* get_rule(TokenType type);
static void parse_precedence(Precedence precedence);


static uint8_t make_literal(Value value) {
    int literal = add_literal(current_chunk(), value);
    if (literal > UINT8_MAX) {
        error("Too many literals in one chunk.");
        return 0;
    }

    return (uint8_t)literal;
}


static void emit_literal(Value value) {
    emit_bytes(OP_LITERAL, make_literal(value));
}


static void end_compiler() {
    emit_return();
#ifdef DEBUG_PRINT_CODE
    if (!parser.had_error) {
        disassemble_chunk(current_chunk(), "code");
    }
#endif
}


static void grouping() {
    expression();
    // TODO: refactor it below to accommodate for all the closures
    consume(TOKEN_RIGHT_PAREN, "Expect ')' after expression.");
}


static void number() {
    double value = strtod(parser.previous.start, NULL);
    emit_literal(NUMBER_VAL(value));
}


static void string() {
    emit_literal(ELEM_VAL(copy_string(parser.previous.start + 1,
                                      parser.previous.length - 2)));
}  


static void literal_simple() {
    switch (parser.previous.type) {
        case TOKEN_NULL: emit_byte(OP_NULL); break;
        case TOKEN_FALSE: emit_byte(OP_FALSE); break;
        case TOKEN_TRUE: emit_byte(OP_TRUE); break;
        default: return;  // should be unreachable
    }
}


ParseRule rules[] = {
    [TOKEN_LEFT_PAREN]      = {grouping, NULL, PREC_NONE},
    [TOKEN_LEFT_SQUARE]     = {grouping, NULL, PREC_NONE},
    [TOKEN_LEFT_ANGLE]      = {grouping, NULL, PREC_NONE},
    [TOKEN_LEFT_CURLY]      = {grouping, NULL, PREC_NONE},
    [TOKEN_RIGHT_PAREN]     = {NULL, NULL, PREC_NONE},
    [TOKEN_RIGHT_SQUARE]    = {NULL, NULL, PREC_NONE},
    [TOKEN_RIGHT_ANGLE]     = {NULL, NULL, PREC_NONE},
    
    [TOKEN_DOT]             = {NULL, NULL, PREC_CALL},
    [TOKEN_COLON]           = {NULL, NULL, PREC_NONE},
    [TOKEN_ASSIGN]          = {NULL, NULL, PREC_ASSIGNMENT},
    [TOKEN_MAIN]            = {NULL, NULL, PREC_NONE},
    [TOKEN_FN]              = {NULL, NULL, PREC_NONE},
    [TOKEN_TYPE]            = {NULL, NULL, PREC_NONE},
    
    [TOKEN_NULL]            = {literal_simple, NULL, PREC_NONE},
    [TOKEN_STRING]          = {string, NULL, PREC_NONE},
    [TOKEN_NUMBER]          = {number, NULL, PREC_NONE},
    [TOKEN_BOOL]            = {NULL, NULL, PREC_NONE},  // define a bool fn
    [TOKEN_TRUE]            = {literal_simple, NULL, PREC_NONE},
    [TOKEN_FALSE]           = {literal_simple, NULL, PREC_NONE},
    [TOKEN_ID]              = {NULL, NULL, PREC_NONE},
    
    [TOKEN_QID]             = {NULL, NULL, PREC_NONE},
    [TOKEN_QBOOL]           = {NULL, NULL, PREC_NONE},
    [TOKEN_QNUMBER]         = {NULL, NULL, PREC_NONE},
    [TOKEN_QTRUE]           = {NULL, NULL, PREC_NONE},
    [TOKEN_QFALSE]          = {NULL, NULL, PREC_NONE},

    [TOKEN_IF]              = {NULL, NULL, PREC_NONE},
    [TOKEN_SELF]            = {NULL, NULL, PREC_NONE},
    [TOKEN_ERROR]           = {NULL, NULL, PREC_NONE},
    [TOKEN_EOF]             = {NULL, NULL, PREC_NONE},    
};


static void parse_precedence(Precedence precedence) {
    advance();
    ParseFn prefix_rule = get_rule(parser.previous.type)->prefix;
    if (prefix_rule == NULL) {
        error("expected expression.");
        return;
    }

    prefix_rule();

    while (precedence <= get_rule(parser.current.type)->precedence) {
        advance();
        ParseFn infix_rule = get_rule(parser.previous.type)->infix;
        infix_rule();
    }

}


static ParseRule* get_rule(TokenType type) {
    return &rules[type];
}


static void expression() {
    parse_precedence(PREC_ASSIGNMENT);
}


bool compile(const char* source, Chunk* chunk) {
    init_scanner(source);
    /*
     * int line = -1;
    for (;;) {
        Token token = scan_token();
        if (token.line != line) {
            printf("%4d ", token.line);
            line = token.line;
        } else {
            printf("  | ");
        }
        printf("%2d '%.*s'\n", token.type, token.length, token.start);

        if (token.type == TOKEN_EOF) break;
    }
    */

    compiling_chunk = chunk;

    parser.had_error = false;
    parser.panic_mode = false;

    advance();
    expression();
    consume(TOKEN_EOF, "Expect end of expression.");
    end_compiler();
    return !parser.had_error;
}

