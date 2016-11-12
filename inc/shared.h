#include <stdint.h>

#define BLOCK_SIZE 32

#define OFFSET_STT 0x3000

#define S_INIT 0
#define S_WAITING 1
#define S_RUNNING 2
#define S_READY 3
#define S_HALT 4

typedef struct __attribute__((aligned(8))) {
    int32_t request_id;
    uint32_t row_id;
    uint32_t col_id;
} Request;
