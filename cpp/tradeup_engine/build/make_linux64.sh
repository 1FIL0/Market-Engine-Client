#* Market Engine Client
#* Copyright (C) 2025 OneFil (1FIL0) https://github.com/1FIL0
#* read LICENCE file - GPL3

cmake -S . -B build_linux64 -DCMAKE_CXX_COMPILER=g++
mkdir -p build_linux64
cd build_linux64
bear -- make -j12
cd ..
