#!/bin/bash

set -e

ESDK=${EPIPHANY_HOME}
ELIBS="-L ${ESDK}/tools/host/lib"
EINCS="-I ${ESDK}/tools/host/include"
ELDF="-T ${ESDK}/bsps/current/internal.ldf"
INC="-I inc/"

# Create binary and output dir
if [ ! -d bin ]; then
  mkdir -p bin
fi
if [ ! -d output ]; then
  mkdir -p output
fi

# Build host app
gcc src/main.c -o bin/main.elf ${INC} ${EINCS} ${ELIBS}\
        -le-hal -le-loader -lpthread

# Build device app
e-gcc ${INC} ${ELDF} $1 src/emain.c -o bin/emain.elf -le-lib -lm
