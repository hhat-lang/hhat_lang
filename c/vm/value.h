#ifndef chat_value_h
#define chat_value_h

#include "common.h"


typedef struct Elem Elem;
typedef struct QElem QElem;

typedef struct CInstr CInstr;
typedef struct QInstr QInstr;
typedef struct QData QData;

typedef struct ElemString ElemString;
typedef struct ElemQBool ElemQBool;
// TODO: implement the QU2, QU3, QU4...


typedef enum {
    VAL_NULL,
    VAL_BOOL,
    VAL_NUMBER,
    VAL_QBOOL,
    VAL_QNUMBER,
    VAL_ELEM,
    VAL_QELEM,
} ValueType;


// struct to remedy classical ops for now
// TODO: refactor it later
typedef struct CInstr {
    uint8_t c_instr;  // 8-bit representation of classical instruction
} CInstr;


typedef struct qdata_t {
    uint8_t qtype;  // value to identify whether it is @bool, @u2, etc. 
    uint8_t data;  // value to hold a single quantum literal
} qdata_t;


typedef struct QInstr {
    uint8_t q_instr;  // 8-bit representation of quantum instruction
} QInstr;


// to represent quantum data as a sequence of instructions
//   (classical or quantum) and also quantum literals
typedef struct QData {
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
        Elem* elem;
        // TODO: think how to place qbool and qnumber here
        // first attempt:
        QData*  qbool;
        QData* qnumber;
        QElem* qelem; 
     } as;
} Value;


// classical
#define IS_NULL(value)    ((value).type == VAL_NULL)
#define IS_BOOL(value)    ((value).type == VAL_BOOL)
#define IS_NUMBER(value)  ((value).type == VAL_NUMBER)

#define IS_ELEM(value)    ((value).type == VAL_ELEM)

// quantum
#define IS_QBOOL(value)   ((value).type == VAL_QBOOL)
#define IS_QNUMBER(value) ((value).type == VAL_QNUMBER)

#define IS_QELEM(value)   ((value).type == VAL_QELEM)

// classical
#define AS_BOOL(value)    ((value).as.boolean)
#define AS_NUMBER(value)  ((value).as.number)
#define AS_ELEM(value)    ((value).as.elem)
// quantum
#define AS_QBOOL(value)   ((value).as.qbool)
#define AS_QNUMBER(value) ((value).as.qnumber)
#define AS_QELEM(value)   ((value).as.qelem)


// classical data
#define NULL_VAL           ((Value){VAL_NULL, {.number = 0}})
#define BOOL_VAL(value)    ((Value){VAL_BOOL, {.boolean = value}})
#define NUMBER_VAL(value)  ((Value){VAL_NUMBER, {.number = value}})
#define ELEM_VAL(value)    ((Value){VAL_ELEM, {.elem = (Elem*)value}})
// quantum data
#define QBOOL_VAL(value)   ((Value){VAL_QBOOL, {.qbool = (qdata_t*)value}})
#define QNUMBER_VAL(value) ((Value){VAL_QNUMBER, {.qnumber = (qdata_t*)value}})
#define QELEM_VAL(value)   ((Value){VAL_QELEM, {.qelem = (QElem*)value}})


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

