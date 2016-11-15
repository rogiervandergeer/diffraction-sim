#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <e-hal.h> 

#include "shared.h"

unsigned rows, cols, i, j, ncores, row, col;

e_platform_t platform;
e_epiphany_t dev;
e_mem_t emem_req;
e_mem_t emem_def;

Request req;
Definition def;

void init_epiphany(e_platform_t * platform) {
    e_init(NULL);
    e_reset_system();
    e_get_platform_info(platform);
}

void init_workgroup(e_epiphany_t * dev) {
    e_return_stat_t result;
    e_open(dev, 0, 0, rows, cols); // Create an epiphany cores workgroup
    e_reset_group(dev);
    result = e_load_group("bin/emain.elf", dev, 0, 0, rows, cols, E_FALSE);
    if(result != E_OK) {
        printf("Error Loading the Epiphany Application %i\n", result);
    }
    e_start_group(dev);
}

double loc(const double diameter, 
                 const unsigned dimension, 
                 const unsigned i) {
    double delta = diameter / dimension;
    return i*delta-(0.5*(dimension-1)*delta);
}


int get_state(const int coreid) {
    int retval;
    e_read(&dev, coreid/4, coreid%4, OFFSET_STT, &retval, sizeof(int));
    return retval;
}

int get_block(const int coreid) {
    OldReq req;
    e_read(&dev, coreid/4, coreid%4, OFFSET_REQ, &req, sizeof(OldReq));
    return req.block_id;
}

void print_status() {
    int coreid;
    fprintf(stdout, "----\n");
    for (coreid=0; coreid<N_CORES; ++coreid) {
        fprintf(stdout, "core %02i:\t%i\t%i\n",
                coreid, get_state(coreid), get_block(coreid));
    }
}

void print_data(const int coreid) {
    Block result;
    e_read(&dev, coreid/4, coreid%4, OFFSET_BLK, 
            &result, sizeof(result));
    OldReq req;
    e_read(&dev, coreid/4, coreid%4, OFFSET_REQ, &req, sizeof(OldReq));
    fprintf(stdout, "block_id %i\n", result.block_id);
    int x;
    for (x=0; x<req.sensor_dimension; ++x) {
        fprintf(stdout, "data %02i: %f,%f\n", 
                x, result.data[x].x, result.data[x].y);
    }
}

void assign(const int coreid, const OldReq* request) {
    e_write(&dev, coreid/4, coreid%4, OFFSET_REQ, request, sizeof(OldReq));
} 

void init() {
    OldReq request;
    request.block_id = 0;
    int coreid;
    for (coreid=0; coreid<N_CORES; ++coreid) {
        assign(coreid, &request);
    }
}

void done(const int coreid) {
    OldReq req;
    req.block_id = -1;
    assign(coreid, &req);
}

int old_read(const int coreid, FILE* fp) {
    OldReq req;
    int got = fscanf(fp, 
            "%i,%i,%i,%lf,%lf,%lf,%lf,%i,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%i,%lf",
            &req.block_id, &req.row_id,
            &req.plate_dimension, &req.plate_diameter, 
            &req.plate_x, &req.plate_y, &req.plate_z,
            &req.sensor_dimension, &req.sensor_diameter,
            &req.sensor_x, &req.sensor_y, &req.sensor_z,
            &req.wavelength,
            &req.platedef_inner, &req.platedef_outer,
            &req.platedef_struts, &req.platedef_strutangle);
    if (got > 0) {
        assign(coreid, &req);
    } else {
        done(coreid);
    }
    return req.block_id;
}

void calc(const PlateDef* pd) {
    int i, j, t;
    double x, y, rsq;
    // TODO: check max dimension
    for (i=0; i<def.plate.dimension; ++i) {
        x = loc(def.plate.diameter, def.plate.dimension, i);
        for (j=0; j<def.plate.dimension; ++j) {
            y = loc(def.plate.diameter, def.plate.dimension, j);
            rsq = x*x + y*y;
            if (rsq < pd->inner_radius * pd->inner_radius) {
                t = 0;
            } else if (rsq > pd->outer_radius * pd->outer_radius) {
                t = 0;
            } else{
                t = 1;
            }
            fprintf(stdout, "x, y, t = %f, %f, %i (rsq=%f)\n", x, y, t, rsq); 
            def.transparency[i*PLATE_SIZE+j] = (char) t;
        }
    }
}


void push_request() {
    // Write a request
    e_write(&emem_req, 0, 0, 0, &req, sizeof(Request));
}

void push_definition() {
    // Write a definition
    e_write(&emem_def, 0, 0, 0, &def, sizeof(Definition));
}

void set_status(const unsigned status) {
    req.status = status;
    push_request();
}

int load_def(FILE* fp) {
    set_status(H_INIT);
    PlateDef pd;
    int vals = fscanf(fp,
        "%i, %i, %lf, %lf, %lf, %lf, %i, %lf, %lf, %lf, %lf, %lf",
        &req.block_id,
        &def.plate.dimension, &def.plate.diameter,
        &def.plate.position.x, &def.plate.position.y, &def.plate.position.z,
        &def.sensor.dimension, &def.sensor.diameter,
        &def.sensor.position.x, &def.sensor.position.y, &def.sensor.position.z,
        &def.wavelength);
    if (vals <= 0) return 0;
    set_status(H_CALC);
    pd.inner_radius = 0;
    pd.outer_radius = 0.05;
    calc(&pd);
    push_definition();
    return 0;
}

void run() { }

int main(int argc, char * argv[]) {

    init_epiphany(&platform);

    rows = platform.rows;
    cols = platform.cols;
    ncores = rows * cols;

    e_alloc(&emem_req, OFFSET_SHA_H, sizeof(Request));
    e_alloc(&emem_def, OFFSET_SHA_H+sizeof(Request), sizeof(Definition));

    FILE *fp;
    fp = fopen("./defs/example.csv", "r");

    while (load_def(fp)) {
        run();
    }

    init_workgroup(&dev);
    init();
    print_status();
    int coreid;
    for (coreid=0; coreid<N_CORES; ++coreid) {
        old_read(coreid, fp);
    }

    int running = 0;
    while (1) {
        for (coreid=0; coreid<N_CORES; ++coreid) {
            if (get_state(coreid) == S_WAITING) {
                print_data(coreid);
                if (old_read(coreid, fp) > 0) running += 1;
            } else if (get_state(coreid) == S_RUNNING) {
                running += 1;
            }
        }
        if (running == 0) break;
        running = 0;
        print_status();
        sleep(2);
    }


    fclose(fp);
    print_status();
    e_close(&dev);
    e_free(&emem_req);
    e_free(&emem_def);
    return 0;
}
