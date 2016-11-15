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

int n_rows, n_cols;

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

void push_request() {
    // Write a request
    e_write(&emem_req, 0, 0, 0, &req, sizeof(Request));
}

void push_definition() {
    // Write a definition
    e_write(&emem_def, 0, 0, 0, &def, sizeof(Definition));
}

void print_status() {
    int coreid;
    fprintf(stdout, "----\n");
    for (coreid=0; coreid<N_CORES; ++coreid) {
        fprintf(stdout, "core %02i:\t%i\t%i\n",
                coreid, get_state(coreid), 42);
    }
}

void clear(const unsigned core) {
    req.order[core] = O_WAIT;
    push_request();
}

void init_sequence() {
    int core;
    for (core=0; core<N_CORES; ++core) {
        req.order[core] = O_INIT;
        req.col_id[core] = -1;
        req.row_id[core] = -1;
        req.pixels[core] = 0;
    }
    push_request();
    for (core=0; core<N_CORES; ++core) {
        while (get_state(core) != S_INIT) { }
        req.order[core] = O_WAIT;
    }
    push_request();
    for (core=0; core<N_CORES; ++core) {
        while (get_state(core) != S_WAIT) { }
    }
}

void halt_sequence() {
    int core;
    for (core=0; core<N_CORES; ++core) {
        req.order[core] = O_HALT;
    }
    push_request();
    for (core=0; core<N_CORES; ++core) {
        while (get_state(core) != S_HALT) { }
    }
}

unsigned n_pixels(col_id) {
    if (col_id == n_cols-1) {
        return def.sensor.dimension-(col_id*BLOCK_SIZE);
    } else {
        return BLOCK_SIZE;
    }
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

void read(const int core_id, FILE* of) {
    Result result;
    e_read(&dev, core_id/4, core_id%4, OFFSET_RES, &result, sizeof(Result));
    fprintf(stdout, "Read   (%03d, %03d) from core %02d (p=%i)\n",
            req.col_id[core_id], req.row_id[core_id], 
            core_id, n_pixels(req.col_id[core_id]));
    int pixel;
    for (pixel=0; pixel<n_pixels(req.col_id[core_id]); ++pixel) {
        fprintf(of, "%i, %i, %i, %lf, %lf\n", 
                req.block_id, req.col_id[core_id]*BLOCK_SIZE+pixel, 
                req.row_id[core_id],
                result.data[pixel].x, result.data[pixel].y);
    }
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
            //        fprintf(stdout, "x, y, t = %f, %f, %i (rsq=%f)\n", x, y, t, rsq); 
            def.transparency[i*PLATE_SIZE+j] = (char) t;
        }
    }
}



int load_def(FILE* fp) {
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
    pd.inner_radius = 0;
    pd.outer_radius = 0.05;
    calc(&pd);
    push_definition();
    return 1;
}

void assign(const unsigned core_id,
        const int col_id, const int row_id) {
    fprintf(stdout, "Assign (%03d, %03d)   to core %02d (p=%i)\n",
            col_id, row_id, core_id, n_pixels(col_id));
    req.order[core_id] = O_RUN;
    req.col_id[core_id] = col_id;
    req.row_id[core_id] = row_id;
    req.pixels[core_id] = n_pixels(col_id);
    push_request();
}

void run(FILE* of) { 
    n_cols = def.sensor.dimension / BLOCK_SIZE;
    n_rows = def.sensor.dimension;
    if (def.sensor.dimension % BLOCK_SIZE > 0) ++n_cols;

    int col_id = 0;
    int row_id = 0;

    while (1) {
        int n_running = 0;
        int core_id;
        for (core_id=0; core_id<N_CORES; ++core_id) {
            if (get_state(core_id) == S_RUN) {
                n_running += 1;
                continue;
            }
            if (get_state(core_id) == S_DONE) {
                read(core_id, of);
                clear(core_id);
            }
            usleep(1);
            if (get_state(core_id) == S_WAIT) {
                if (col_id < n_cols) {
                    assign(core_id, col_id, row_id);
                    ++row_id;
                    if (row_id == n_rows) {
                        row_id = 0;
                        ++col_id;
                    }
                    n_running += 1;
                }
            }
        }
        if ((n_running == 0) && (col_id >= n_cols)) break;
        usleep(100);
    }
    fprintf(stdout, "Done.\n");
}

int main(int argc, char * argv[]) {

    // Handle arguments and open files
    if (argc != 3) {
        printf("Usage: %s <definition> <output>\n", argv[0]);
        return 1;
    }
    FILE *input_file, *output_file;
    input_file = fopen(argv[1], "r");
    if (!input_file) {
        printf("Unable to open '%s' for reading.\n", argv[1]);
        return 2;
    }
    output_file = fopen(argv[2], "w");
    if (!output_file) {
        printf("Unable to open '%s' for writing.\n", argv[2]);
        return 2;
    }

    init_epiphany(&platform);

    rows = platform.rows;
    cols = platform.cols;
    ncores = rows * cols;

    e_alloc(&emem_req, OFFSET_SHA_H, sizeof(Request));
    e_alloc(&emem_def, OFFSET_SHA_H+sizeof(Request), sizeof(Definition));

    init_workgroup(&dev);
    init_sequence();

    while (load_def(input_file)) {
        run(output_file);
    }

    fclose(input_file);
    fclose(output_file);
    halt_sequence();
    e_close(&dev);
    e_free(&emem_req);
    e_free(&emem_def);
    return 0;
}
