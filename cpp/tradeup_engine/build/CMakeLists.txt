cmake_minimum_required(VERSION 3.10)
project(engine)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(OpenMP REQUIRED)
find_package(OpenSSL REQUIRED)
#find_package(OpenCL REQUIRED)
message(STATUS "OpenSSL include dirs: ${OPENSSL_INCLUDE_DIR}")
message(STATUS "OpenSSL libraries: ${OPENSSL_LIBRARIES}")

# EMBED GPU KERNEL START
set(GPU_KERNEL_CL_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../src/gpu_kernel_cl)
set(GPU_KERNEL_HPP_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../src/gpu_kernel_embedded)

set(CL_KERNEL_SOURCE ${GPU_KERNEL_CL_DIR}/kernel.cl)
get_filename_component(KERNEL_NAME_WE ${CL_KERNEL_SOURCE} NAME_WE)
set(GPU_EMBEDDED_HEADER_FILE ${GPU_KERNEL_HPP_DIR}/${KERNEL_NAME_WE}_cl_embedded.hpp)
set(GPU_PREPROCESSED_CL_FILE ${GPU_KERNEL_HPP_DIR}/${KERNEL_NAME_WE}_cl_preprocessed.hpp)
add_custom_command(
    OUTPUT ${GPU_EMBEDDED_HEADER_FILE}
    COMMAND echo "Preprocessing and embedding GPU kernel: ${CL_KERNEL_SOURCE}"
    COMMAND mkdir -p $GPU_KERNEL_HPP_DIR
    COMMAND cpp -P ${CL_KERNEL_SOURCE} -o ${GPU_PREPROCESSED_CL_FILE}
    COMMAND xxd -n "kernel_cl_hpp_${KERNEL_NAME_WE}" -i ${GPU_PREPROCESSED_CL_FILE} > ${GPU_EMBEDDED_HEADER_FILE}
    DEPENDS ${CL_KERNEL_SOURCE}
    VERBATIM
)
list(APPEND GENERATED_HEADERS ${GPU_EMBEDDED_HEADER_FILE})
add_custom_target(embed_gpu_kernels ALL DEPENDS ${GENERATED_HEADERS})
# EMBED GPU KERNEL END

file(GLOB CALCULATOR_DIRS ${CMAKE_SOURCE_DIR}/../src/*)
file(GLOB SHARED_DIRS ${CMAKE_SOURCE_DIR}/../../../../market_engine_share/cpp/share/src/*)
include_directories(${CALCULATOR_DIRS})
include_directories(${SHARED_DIRS})

file(GLOB_RECURSE SOURCES_CALCULATOR
    "../src/*.cpp"
)

file(GLOB_RECURSE SOURCES_SHARE
    "../../../../market_engine_share/cpp/share/src/*.cpp"
)

add_executable(engine ${SOURCES_CALCULATOR} ${SOURCES_SHARE})

if (CMAKE_SYSTEM_NAME STREQUAL "Linux")
    target_link_libraries(engine PRIVATE OpenMP::OpenMP_CXX OpenCL OpenSSL::Crypto)
    target_compile_options(engine PRIVATE -fopenmp -O2 -Wall -Wextra)
    target_link_options(engine PRIVATE -fopenmp)
else()
    target_link_libraries(engine PRIVATE 
        OpenMP::OpenMP_CXX 
        OpenCL::OpenCL 
        OpenSSL::Crypto
    )

    target_compile_options(engine PRIVATE -fopenmp -O2 -Wall -Wextra)
    target_link_options(engine PRIVATE -fopenmp)
endif()
