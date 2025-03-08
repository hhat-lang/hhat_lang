#include <stdio.h>
#include <string.h>
#include "common.h"
#include "scanner.h"


typedef struct {
    const char* start;
    const char* current;
    int line;
} Scanner;


Scanner scanner;


void init_scanner(const char* source) {
    scanner.start = source;
    scanner.current = source;
    scanner.line = 1;
}


static bool is_quantum(char c) {
    return c == '@';
}


static bool is_alpha(char c) {
    return (c >= 'a' && c <= 'z') ||
           (c >= 'A' && c <= 'Z') ||
           c == '_';
}


static bool is_digit(char c) {
    return c >= '0' && c <= '9';
}


bool is_at_end() {
    return *scanner.current == '\0';
}


static char advance() {
    scanner.current++;
    return scanner.current[-1];
}


static char peek() {
    return *scanner.current;
}


static char peek_next() {
    if (is_at_end()) return '\0';
    return scanner.current[1];
}


static Token make_token(TokenType type) {
    Token token;
    token.type = type;
    token.start = scanner.start;
    token.length = (int)(scanner.current - scanner.start);
    token.line = scanner.line;
    return token;
}


static Token error_token(const char* message) {
    Token token;
    token.type = TOKEN_ERROR;
    token.start = message;
    token.length = (int)strlen(message);
    token.line = scanner.line;
    return token;
}


static void skip_whitespace() {
    for (;;) {
        char c = peek();
        switch (c) {
            case ' ':
            case ',':
            case ';':
            case '\r':
            case '\t':
                advance();
                break;
            case '\n':
                scanner.line++;
                advance();
                break;
            case '/':
                if (peek_next() == '/') {
                    while(peek() != '\n' && !is_at_end()) advance();
                } else {
                    return;
                }
                break;    
            default:
                return;
        }
    }
}


static TokenType check_kw(int start, int length, const char* rest, TokenType type) {
    if (scanner.current - scanner.start == start + length && memcmp(scanner.start + start, rest, length) == 0) {
        return type;
    }

    return TOKEN_ID;
}


static TokenType _sub_identifier_type(int pos) {
    switch (scanner.start[pos]) {
        case 'm': return check_kw(1, 3, "ain", TOKEN_MAIN);
        case 'f':
            if (scanner.current - scanner.start == 1) return check_kw(1, 1, "n", TOKEN_FN); 
            if (scanner.current - scanner.start > 1) {
                switch (scanner.start[1]) {
                    case 'a': return check_kw(2, 3, "lse", TOKEN_FALSE);
                }
            }
            break;    
        case 't':
            if (scanner.current - scanner.start > 1) {
                switch  (scanner.start[1]) {
                    case 'y': return check_kw(2, 2, "pe", TOKEN_TYPE);
                    case 'r': return check_kw(2, 2, "ue", TOKEN_TRUE);         
                }
            }
            break;
    }
    return TOKEN_ID;
}


static TokenType identifier_type() {
    return _sub_identifier_type(0);   
}


static TokenType qidentifier_type() {
    if (is_quantum(scanner.start[0])) {
        TokenType tt = _sub_identifier_type(1);
        switch (tt) {
            case TOKEN_TRUE: return TOKEN_QTRUE;
            case TOKEN_FALSE: return TOKEN_QFALSE;
            default: break; 
        }                 
    }
    return TOKEN_ERROR;
}


static Token identifier() {
    while (is_alpha(peek()) || is_digit(peek())) advance();
    return make_token(identifier_type());
}


static Token qidentifier() {
    advance();
    while (is_alpha(peek()) || is_digit(peek())) advance();
    return make_token(qidentifier_type());
}


static Token number() {
    while (is_digit(peek())) advance();

    if (peek() == '.' && is_digit(peek_next())) {
        advance();

        while (is_digit(peek())) advance();
    }

    return make_token(TOKEN_NUMBER);
}


static Token qnumber() {
    advance();
    while (is_digit(peek())) advance();
     
    if (peek() == '.' && is_digit(peek_next())) {
        advance();

        while (is_digit(peek())) advance();
    }

    return make_token(TOKEN_QNUMBER);
}
       

Token string() {
    while (peek() != '"' && !is_at_end()) {
        if (peek() == '\n') scanner.line++;
        advance();
    }

    if (is_at_end()) return error_token("unterminated string.");

    advance();
    return make_token(TOKEN_STRING);
}


Token scan_token() {
    skip_whitespace();
    scanner.start = scanner.current;

    if (is_at_end()) return make_token(TOKEN_EOF);
    
    char c = advance();
    if (is_alpha(c)) return identifier();
    if (is_digit(c)) return number();
    if (is_quantum(c)) {
        if (is_alpha(peek_next())) return qidentifier();
        if (is_digit(peek_next())) return qnumber();
    }                

    switch (c) {
        case '{': return make_token(TOKEN_LEFT_CURLY);
        case '}': return make_token(TOKEN_RIGHT_CURLY);
        case '(': return make_token(TOKEN_LEFT_PAREN);
        case ')': return make_token(TOKEN_RIGHT_PAREN);
        case '[': return make_token(TOKEN_LEFT_SQUARE);
        case ']': return make_token(TOKEN_RIGHT_SQUARE);
        case '<': return make_token(TOKEN_LEFT_ANGLE);
        case '>': return make_token(TOKEN_RIGHT_ANGLE);
        case ':': return make_token(TOKEN_COLON);
        case '=': return make_token(TOKEN_ASSIGN);
        case '.': return make_token(TOKEN_DOT);
        case '"': return string();
    }

    return error_token("unexpected character.");
}
