#ifndef chat_elem_h
#define chat_elem_h


#include "common.h"
#include "value.h"


#define ELEM_TYPE(value)     (AS_ELEM(value)->type)
#define QELEM_TYPE(value)    (AS_QELEM(value)->type)

// classical
#define IS_STRING(value)     (is_elem_type(value, ELEM_STRING))

#define AS_STRING(value)     ((ElemString*)AS_ELEM(value))

// quantum
//#define IS_QBOOL(value)      (is_elem_type(value, ELEM_QBOOL))
#define IS_QU2(value)        (is_elem_qtype(value, ELEM_QU2))
#define IS_QU3(value)        (is_elem_qtype(value, ELEM_QU3))
#define IS_QU4(value)        (is_elem_qtype(value, ELEM_QU4))

//#define AS_QBOOL(value)      ((ElemQBool*)AS_QELEM(value))



typedef enum {
    ELEM_STRING,
} ElemType;


typedef enum {
    ELEM_QBOOL,
    ELEM_QU2,
    ELEM_QU3,
    ELEM_QU4,
} QElemType;


struct Elem {
    ElemType type;
};


struct QElem {
    QElemType type;
};


struct ElemString {
    Elem elem;
    int length;
    char* chars;
};


struct ElemQBool {
    QElem qelem;
    int length;
    char* chars;
    // TODO: include what more is needed for quantum data
};


ElemString* copy_string(const char* chars, int length);


static inline bool is_elem_type(Value value, ElemType type) {
    return IS_ELEM(value) && AS_ELEM(value)->type == type;
}


static inline bool is_elem_qtype(Value value, QElemType qtype) {
    return IS_QELEM(value) && AS_QELEM(value)->type == qtype;
}


#endif
