#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <e-hal.h> 

#include "shared.h"

unsigned rows, cols, i, j, ncores, row, col;

e_platform_t platform;
e_epiphany_t dev;
e_mem_t emem;

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

int get_state(const int coreid) {
    int retval;
    e_read(&dev, coreid/4, coreid%4, OFFSET_STT, &retval, sizeof(int));
    return retval;
}

int get_block(const int coreid) {
    Request req;
    e_read(&dev, coreid/4, coreid%4, OFFSET_REQ, &req, sizeof(Request));
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
    Request req;
    e_read(&dev, coreid/4, coreid%4, OFFSET_REQ, &req, sizeof(Request));
    fprintf(stdout, "block_id %i\n", result.block_id);
    int x;
    for (x=0; x<req.sensor_dimension; ++x) {
        fprintf(stdout, "data %02i: %f,%f\n", 
                x, result.data[x].x, result.data[x].y);
    }
}

void assign(const int coreid, const Request* request) {
    e_write(&dev, coreid/4, coreid%4, OFFSET_REQ, request, sizeof(Request));
} 

void init() {
    Request request;
    request.block_id = 0;
    int coreid;
    for (coreid=0; coreid<N_CORES; ++coreid) {
        assign(coreid, &request);
    }
}

void done(const int coreid) {
    Request req;
    req.block_id = -1;
    assign(coreid, &req);
}

int read(const int coreid, FILE* fp) {
    Request req;
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

int main(int argc, char * argv[]) {

    init_epiphany(&platform);

    rows = platform.rows;
    cols = platform.cols;
    ncores = rows * cols;

    FILE *fp;
    fp = fopen("./defs/example.csv", "r");

    init_workgroup(&dev);
    init();
    print_status();
    int coreid;
    for (coreid=0; coreid<N_CORES; ++coreid) {
        read(coreid, fp);
    }

    int running = 0;
    while (1) {
        for (coreid=0; coreid<N_CORES; ++coreid) {
            if (get_state(coreid) == S_WAITING) {
                print_data(coreid);
                if (read(coreid, fp) > 0) running += 1;
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
    return 0;
}
