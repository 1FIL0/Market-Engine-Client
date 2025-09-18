#* Market Engine Client
#* Copyright (C) 2025 OneFil (1FIL0) https://github.com/1FIL0
#*
#* This program is free software: you can redistribute it and/or modify
#* it under the terms of the GNU General Public License as published by
#* the Free Software Foundation, either version 3 of the License, or
#* (at your option) any later version.
#*
#* This program is distributed in the hope that it will be useful,
#* but WITHOUT ANY WARRANTY; without even the implied warranty of
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#* GNU General Public License for more details.
#*
#* You should have received a copy of the GNU General Public License
#* along with this program.  If not, see <http://www.gnu.org/licenses/>.
#* read LICENCE file


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

file(REMOVE_RECURSE ${GPU_KERNEL_HPP_DIR})
file(MAKE_DIRECTORY ${GPU_KERNEL_HPP_DIR})
add_custom_command(
    OUTPUT ${GPU_EMBEDDED_HEADER_FILE}
    COMMAND ${CMAKE_COMMAND} -E echo "Preprocessing and embedding GPU kernel: ${CL_KERNEL_SOURCE}"
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
add_dependencies(engine embed_gpu_kernels)

if (CMAKE_SYSTEM_NAME STREQUAL "Linux")
    target_link_libraries(engine PRIVATE OpenMP::OpenMP_CXX OpenCL OpenSSL::Crypto)
    target_compile_options(engine PRIVATE -fopenmp -O2 -Wall -Wextra )
    target_link_options(engine PRIVATE -fopenmp)
else()
    target_link_libraries(engine PRIVATE OpenMP::OpenMP_CXX OpenCL OpenSSL::Crypto)
    target_compile_options(engine PRIVATE -fopenmp -O2 -Wall -Wextra)
    target_link_options(engine PRIVATE -mwindows)
endif()
