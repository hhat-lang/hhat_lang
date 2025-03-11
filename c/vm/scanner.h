#ifndef chat_scanner_h
#define chat_scanner_h


typedef enum {
    // single-char tokens
    TOKEN_LEFT_PAREN, TOKEN_RIGHT_PAREN,
    TOKEN_LEFT_SQUARE, TOKEN_RIGHT_SQUARE,
    TOKEN_LEFT_CURLY, TOKEN_RIGHT_CURLY,
    TOKEN_LEFT_ANGLE, TOKEN_RIGHT_ANGLE,
    TOKEN_DOT, TOKEN_COLON, TOKEN_ASSIGN,
    // literals
    TOKEN_ID, TOKEN_QID, TOKEN_STRING, TOKEN_BOOL, TOKEN_NUMBER, TOKEN_QBOOL, TOKEN_QNUMBER,
    // keywords
    TOKEN_FN, TOKEN_TYPE, TOKEN_MAIN, TOKEN_IF, TOKEN_SELF,
    TOKEN_TRUE, TOKEN_FALSE, TOKEN_QTRUE, TOKEN_QFALSE, TOKEN_NULL,

    // others
    TOKEN_ERROR, TOKEN_EOF
} TokenType;


typedef struct {
    TokenType type;
    const char* start;
    int length;
    int line;
} Token;


void init_scanner(const char* source);
Token scan_token();


#endif
