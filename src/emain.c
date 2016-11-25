#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <e-lib.h> // Epiphany cores library

#include "shared.h"

int* state;
Request* volatile req;
Result* res;
int core_id;

void calc_core_id(void) {
    // Calculate the core number;
    unsigned core_row = e_group_config.core_row;
    unsigned core_col = e_group_config.core_col;
    unsigned group_rows = e_group_config.group_rows;
    unsigned group_cols = e_group_config.group_cols;
    core_id = core_row * group_cols + core_col;
}


int get_order(void) {
    return req->order[core_id];
}

void set_state(const int status) {
    *state = status;
}

double d1, d2;
float dc;
int i, j, q;
Vector laser, plate, sensor;

double middle, strut_radius, strut_angle, rsq, ang;

double transparency(const Definition* d,
        const unsigned i,
        const unsigned j) {
    int val = (int)d->transparency[i*PLATE_SIZE+j];
    return (float)val/255.;
}


double dim(const double delta, const unsigned n, const unsigned i) {
    return i*delta-(0.5*delta*(n-1));
}

double distance_mod(const Vector* a, const Vector* b, const double inv_wl) {
    return fmod(
        sqrt(
            (a->x - b->x)*(a->x - b->x) +
            (a->y - b->y)*(a->y - b->y) +
            (a->z - b->z)*(a->z - b->z)
        )*inv_wl, 2*M_PI);
}

void clear_result(void) {
    for (i=0; i<BLOCK_SIZE; ++i) {
        res->data[i].x = 0.;
        res->data[i].y = 0.;
    }
    res->block_id = -1;
}

void process() { 
    set_state(S_RUN);
    clear_result();

    Definition* def = (Definition*) (OFFSET_SHA_C+sizeof(Request));

    // Laser
    laser.x = 0;
    laser.y = 0;
    laser.z = 0;

    // Plate
    double plate_delta = def->plate.diameter / def->plate.dimension;
    plate.x = def->plate.position.x;
    plate.y = def->plate.position.y;
    plate.z = def->plate.position.z;

    // Sensor
    double sensor_delta = def->sensor.diameter / def->sensor.dimension;
    sensor.x = def->sensor.position.x;
    sensor.y = def->sensor.position.y
        + dim(sensor_delta, def->sensor.dimension, req->row_id[core_id]);
    sensor.z = def->sensor.position.z;


    int q_start = req->col_id[core_id] * BLOCK_SIZE;
    int q_end = q_start + req->pixels[core_id];
    double wl = 1./(def->wavelength);

    for (i=0; i<def->plate.dimension; ++i) {
        plate.x = def->plate.position.x
            + dim(plate_delta, def->plate.dimension, i);
        for (j=0; j<def->plate.dimension; ++j) {
            plate.y = def->plate.position.y
                + dim(plate_delta, def->plate.dimension, j);
            double t = transparency(def, i, j);
            if (t > 0) {
                d1 = distance_mod(&laser, &plate, wl);
                for (q=q_start; q<q_end; ++q) {
                    sensor.x = def->sensor.position.x
                        + dim(sensor_delta, def->sensor.dimension, q);
                    d2 = distance_mod(&plate, &sensor, wl);
                    dc = (float)(d1+d2);
//                    float dx = (float)dc;
//                    double sx = (double) sinf(dx);
                    float sx, cx;
                    sincosf(dc, &sx, &cx);
                    res->data[q-q_start].x += (double)sx;
                    res->data[q-q_start].y += (double)cx;
                }
            }
        }
    }
    res->block_id = req->block_id;

    set_state(S_DONE);
    while (get_order() == O_RUN) e_wait(0, 1000);


    set_state(S_WAIT);
    req->block_id = 0;
    return;
}


int main(void) {
    state = (int*) OFFSET_STT;
    req = (Request* volatile) OFFSET_SHA_C;
    res = (Result*) OFFSET_RES;
    calc_core_id();

    set_state(S_INIT);
    while (get_order() != O_INIT) e_wait(0, 1000);
    while (get_order() == O_INIT) e_wait(0, 1000);
    set_state(S_WAIT);

    while (get_order() != O_HALT) {
        if (get_order() == O_WAIT) {
            e_wait(0, 10000);
        } else if (get_order() == O_RUN) {
            process();
        } 
    }
    set_state(S_HALT);
}
