#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <e-hal.h>

#include "shared.h"


void init_epiphany() {
    e_init(NULL);
    e_reset_system();
}

void init_workgroup(e_epiphany_t* dev) {
    e_return_stat_t result;
    e_open(dev, 0, 0, 4, 4);
    e_reset_group(dev);
    result = e_load_group("bin/emain.elf", dev, 0, 0, 4, 4, E_FALSE);
    if (result != E_OK) {
        printf("Error loading application %i\n", result);
    }
    e_start_group(dev);
}


int main(int argc, char* argv[]) {
    init_epiphany();
    e_epiphany_t dev;
    init_workgroup(&dev);

    

    e_close(&dev);
    return 0;
}
