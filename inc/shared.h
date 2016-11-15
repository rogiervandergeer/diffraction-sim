#include <stdint.h>

#define BLOCK_SIZE 64
#define PLATE_SIZE 25
#define BUFOFFSET (0x01000000)
#define N_CORES 5

#define OFFSET_STT 0x6000
#define OFFSET_REQ 0x6500
#define OFFSET_BLK 0x7000

#define OFFSET_SHA_H 0x01000000
#define OFFSET_SHA_C 0x8f000000

#define S_INIT 0
#define S_WAITING 1
#define S_RUNNING 2
#define S_DONE 3

#define H_INIT 0
#define H_CALC 1
#define H_WAIT 2
#define H_DONE 3

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
    uint32_t status;
    int32_t block_id;
    int32_t col_id[N_CORES];
    int32_t row_id[N_CORES];
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
    uint32_t volatile row_id;
    uint32_t volatile plate_dimension;
    double volatile plate_diameter;
    double volatile plate_x;
    double volatile plate_y;
    double volatile plate_z;
    uint32_t volatile sensor_dimension;
    double volatile sensor_diameter;
    double volatile sensor_x;
    double volatile sensor_y;
    double volatile sensor_z;
    double volatile wavelength;
    double volatile platedef_inner;
    double volatile platedef_outer;
    uint32_t volatile platedef_struts;
    double volatile platedef_strutangle;
} OldReq;

typedef struct __attribute__((aligned(8))) {
    int32_t volatile block_id;
    Field volatile data[BLOCK_SIZE];
} Block;
