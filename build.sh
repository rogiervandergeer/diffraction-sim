#!/bin/bash

set -e

ESDK=${EPIPHANY_HOME}
ELIBS="-L ${ESDK}/tools/host/lib"
EINCS="-I ${ESDK}/tools/host/include"
ELDF="-T ${ESDK}/bsps/current/internal.ldf"
INC="-I inc/"

# Create binary dir
if [ ! -d bin ]; then
  mkdir -p bin
fi

# Build host app
gcc src/main.c -o bin/main.elf ${INC} ${EINCS} ${ELIBS}\
        -le-hal -le-loader -lpthread

# Build device app
e-gcc ${INC} ${ELDF} -O0 src/emain.c -o bin/emain.elf -le-lib -lm
