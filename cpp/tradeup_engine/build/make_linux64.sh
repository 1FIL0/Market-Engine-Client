cmake -S . -B build_linux64 -DCMAKE_CXX_COMPILER=g++
mkdir -p build_linux64
cd build_linux64
bear -- make -j12
cd ..
