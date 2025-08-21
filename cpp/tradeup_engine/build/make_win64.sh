rm ../src/gpu_kernel_embedded/*
cmake -S . -B build_win64 -G "Unix Makefiles" -DCMAKE_CXX_COMPILER=g++
mkdir -p build_win64
cd build_win64
make -j12
cd ..