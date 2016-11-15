#include <stdint.h>

#define BLOCK_SIZE 64
#define PLATE_SIZE 2750
#define BUFOFFSET (0x01000000)
#define N_CORES 16

#define OFFSET_STT 0x6000
#define OFFSET_REQ 0x6500
#define OFFSET_RES 0x7000

#define OFFSET_SHA_H 0x01000000
#define OFFSET_SHA_C 0x8f000000

#define S_INIT 0
#define S_WAIT 1
#define S_RUN 2
#define S_DONE 3
#define S_HALT 5

#define O_INIT 0
#define O_WAIT 1
#define O_RUN 2
#define O_HALT 5

typedef struct __attribute__((aligned(8))) {
    double x;
    double y;
    double z;
} Vector;

typedef struct __attribute__((aligned(8))) {
    double x;
    double y;
} Field;

typedef struct __attribute__((aligned(8))) {
    uint32_t dimension;
    double diameter;
    Vector position;
} Raster;

typedef struct __attribute__((aligned(8), packed)) {
    int32_t block_id;
    int32_t order[N_CORES];
    int32_t col_id[N_CORES];
    int32_t row_id[N_CORES];
    int32_t pixels[N_CORES];
} Request;

typedef struct __attribute__((aligned(8))) {
    Raster plate;
    Raster sensor;
    double wavelength;
    char transparency[PLATE_SIZE*PLATE_SIZE];
} Definition;

typedef struct {
    double inner_radius;
    double outer_radius;
} PlateDef;

typedef struct __attribute__((aligned(8))) {
    int32_t volatile block_id;
    Field volatile data[BLOCK_SIZE];
} Result;
