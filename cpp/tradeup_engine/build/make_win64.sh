#* Market Engine Client
#* Copyright (C) 2025 OneFil (1FIL0) https://github.com/1FIL0
#* read LICENCE file - GPL3

rm ../src/gpu_kernel_embedded/*
cmake -S . -B build_win64 -G "MinGW Makefiles" -DCMAKE_CXX_COMPILER=g++
mkdir -p build_win64
cd build_win64
mingw32-make -j12
cd ..