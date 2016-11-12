#!/bin/bash

set -e

ESDK=${EPIPHANY_HOME}
ELIBS="-L ${ESDK}/tools/host/lib"
EINCS="-I ${ESDK}/tools/host/include"
ELDF=${ESDK}/bsps/current/internal.ldf

# Create binary dir
if [ ! -d bin ]; then
  mkdir -p bin
fi

# Build host app
gcc main.c -o bin/main.elf ${EINCS} ${ELIBS} -le-hal -le-loader -lpthread

# Build device app
e-gcc -T ${ELDF} -O0 emain.c -o emain.elf -le-lib -lm
