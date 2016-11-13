#include <stdint.h>

#define BLOCK_SIZE 64
#define BUFOFFSET (0x01000000)
#define N_CORES 5

#define OFFSET_STT 0x6000
#define OFFSET_REQ 0x6500
#define OFFSET_BLK 0x7000

#define S_INIT 0
#define S_WAITING 1
#define S_RUNNING 2
#define S_DONE 3

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
} Request;

typedef struct __attribute__((aligned(8))) {
    int32_t volatile block_id;
    Field volatile data[BLOCK_SIZE];
} Block;
