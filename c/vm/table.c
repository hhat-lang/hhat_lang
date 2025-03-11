#include <stdlib.h>
#include <string.h>
#include "memory.h"
#include "elem.h"
#include "table.h"
#include "value.h"


void init_table(Table* table) {
  table->count = 0;
  table->max = 0;
  table->entries = NULL;
}


