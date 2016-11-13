#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <e-lib.h> // Epiphany cores library

#include "shared.h"

Request* req = (Request*) OFFSET_REQ;
double d1, d2;
int i, j, q;
Vector laser, plate, sensor;

double middle, strut_radius, strut_angle, rsq, ang;

double calc_strut_position(const int i) {
    return 2*i*M_PI/req->platedef_struts - M_PI + req->platedef_strutangle;
}

bool transparent(const Vector* p) {
    double rsq = (p->x * p->x) + (p->y * p->y);
    if (rsq > (req->platedef_outer * req->platedef_outer)) return false;
    if (rsq < (req->platedef_inner * req->platedef_inner)) return false;
    return true;
    /*if (req->platedef_struts == 0) return true;
    bool retval = true;
    ang = atan2(p->y, p->x);
    strut_radius = (req->platedef_outer - req->platedef_inner)/2;
    strut_angle = (req->platedef_outer + req->platedef_inner)/2;
    for (q=0; q<req->platedef_struts+1; ++q) {
         double strut_position = calc_strut_position(q); 
         if (
    }
    return retval;*/
}


float dim(const double delta, const unsigned n, const unsigned i) {
    return i*delta-(0.5*delta*(n-1));
}

double distance(const Vector* a, const Vector* b) {
    return sqrt(
        (a->x - b->x)*(a->x - b->x) +
        (a->y - b->y)*(a->y - b->y) +
        (a->z - b->z)*(a->z - b->z)
    )/req->wavelength;
}

void process(Block* result) { 
    e_wait(0, 10000000);
    for (i=0; i<BLOCK_SIZE; ++i) {
        result->data[i].x = 0.;
        result->data[i].y = 0.;
    }
    result->block_id = -1;

    laser.x = 0;
    laser.y = 0;
    laser.z = 0;
    double plate_delta = req->plate_diameter / req->plate_dimension;
    plate.x = req->plate_x;
    plate.y = req->plate_y;
    plate.z = req->plate_z;
    double sensor_delta = req->sensor_diameter / req->sensor_dimension;
    sensor.x = req->sensor_x;
    sensor.y = req->sensor_y + 
        dim(sensor_delta, req->sensor_dimension, req->row_id);
    sensor.z = req->sensor_z;;

    for (i=0; i<req->plate_dimension; ++i) {
        for (j=0; j<req->plate_dimension; ++j) {
            plate.x = req->plate_x + 
                dim(plate_delta, req->plate_dimension, i);
            plate.y = req->plate_y +
                dim(plate_delta, req->plate_dimension, j);
            // TODO: make opacity independent of plate position
            if (transparent(&plate)) {
                d1 = distance(&laser, &plate);                
                for (q=0; q<req->sensor_dimension; ++q) {
                    sensor.x = dim(sensor_delta, req->sensor_dimension, q);
                    d2 = distance(&plate, &sensor);
                    result->data[q].x += sin(d1+d2);
                    result->data[q].y += cos(d1+d2);
                }
            }
        }
    }

    result->block_id = req->block_id;
    req->block_id = 0;
    return;
}

int main(void) {
    int* state = (int*) OFFSET_STT;
    Block* data = (Block*) OFFSET_BLK;
    *state = S_INIT;
    while (req->block_id != 0) { }
    *state = S_WAITING;
    while (1) {
        while (req->block_id == 0) { }
        if (req->block_id < 0) break;
        *state = S_RUNNING;
        process(data);
        *state = S_WAITING;
    }
    *state = S_DONE;
}
