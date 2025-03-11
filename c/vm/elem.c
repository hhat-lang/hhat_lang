#include <stdio.h>
#include <string.h>
#include "memory.h"
#include "elem.h"
#include "value.h"
#include "vm.h"


#define ALLOCATE_ELEM(type, elem_type) \
    (type*)allocate_elem(sizeof(type), elem_type)


static Elem* allocate_elem(size_t size, ElemType type) {
    Elem* elem = (Elem*)reallocate(NULL, 0, size);
    elem->type = type;
    return elem;
}


static ElemString* allocate_string(char* chars, int length) {
    ElemString* string = ALLOCATE_ELEM(ElemString, ELEM_STRING);
    string->length = length;
    return string;
}


ElemString* copy_string(const char* chars, int length) {
    char* heap_chars = ALLOCATE(char, length + 1);
    memcpy(heap_chars, chars, length);
    heap_chars[length] = '\0';
    return allocate_string(heap_chars, length);
}


