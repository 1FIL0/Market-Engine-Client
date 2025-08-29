rm ../src/gpu_kernel_embedded/*
cmake -S . -B build_win64 -G "MinGW Makefiles" -DCMAKE_CXX_COMPILER=g++
mkdir -p build_win64
cd build_win64
mingw32-make -j12
cd ..