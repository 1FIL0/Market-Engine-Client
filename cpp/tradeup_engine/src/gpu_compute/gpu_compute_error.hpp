#pragma once

#include "namespace.hpp"
#include <string>

#define CL_TARGET_OPENCL_VERSION 300
#define CL_HPP_TARGET_OPENCL_VERSION 300
#define CL_HPP_ENABLE_EXCEPTIONS
#include <CL/opencl.hpp>

START_ENGINE_NAMESPACE_MULTI(COMPGPU)

std::string getCLError(const cl::Error &error);

END_ENGINE_NAMESPACE