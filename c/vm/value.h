#ifndef chat_value_h
#define chat_value_h

#include "common.h"


typedef enum {
    VAL_NULL,
    VAL_BOOL,
    VAL_NUMBER,
    VAL_QBOOL,
    VAL_QNUMBER,
} ValueType;


// struct to remedy classical ops for now
// TODO: refactor it later
typedef struct {
    uint8_t c_instr;
} CInstr;


typedef struct {
    uint8_t qtype;
    uint8_t data;
} qdata_t;


typedef struct {
    uint8_t q_instr;
} QInstr;


// to represent quantum data as a sequence of instructions
//   (classical or quantum) and also quantum literals
typedef struct {
    union {
        CInstr cop;
        QInstr qop;
        qdata_t qliteral;
    } as;
    QData* next;
} QData;


typedef struct {
    ValueType type;
    union {
        bool boolean;
        double number;
        // TODO: think how to place qbool and qnumber here
        // first attempt:
        qdata_t qbool;
        qdata_t qnumber; 
     } as;
} Value;


#define IS_NULL(value)    ((value).type == VAL_NULL)
#define IS_BOOL(value)    ((value).type == VAL_BOOL)
#define IS_NUMBER(value)  ((value).type == VAL_NUMBER)
#define IS_QBOOL(value)   ((value).type == VAL_QBOOL)
#define IS_QNUMBER(value) ((value).type == VAL_QNUMBER)

#define AS_BOOL(value)    ((value).as.boolean)
#define AS_NUMBER(value)  ((value).as.number)
#define AS_QBOOL(value)   ((value).as.qbool)
#define AS_QNUMBER(value) ((value).as.qnumber)


// classical data
#define NULL_VAL(value) ((Value){VAL_NULL, {.number = 0}})
#define BOOL_VAL(value) ((Value){VAL_BOOL, {.boolean = value}})
#define NUMBER_VAL(value) ((Value){VAL_NUMBER, {.number = value}})
// quantum data
#define QBOOL_VAL(value) ((Value){VAL_QBOOL, {.qbool = {.qtype = 0x1, .data = value}}})
#define QNUMBER_VAL(value) ((Value){VAL_QNUMBER, {.qnumber = {.qtype = 0x2, .data = value}}})


typedef struct {
    int max;
    int count;
    Value* values;
} ValueArray;


void init_value_array(ValueArray* array);
void write_value_array(ValueArray* array, Value value);
void free_value_array(ValueArray* array);
void print_value(Value value);


#endif

