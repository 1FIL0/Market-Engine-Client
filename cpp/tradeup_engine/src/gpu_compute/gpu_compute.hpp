#pragma once

#define CL_TARGET_OPENCL_VERSION 300
#define CL_HPP_TARGET_OPENCL_VERSION 300
#define CL_HPP_ENABLE_EXCEPTIONS

#include "namespace.hpp"
#include <CL/cl_platform.h>
#include <CL/opencl.hpp>

START_ENGINE_NAMESPACE_MULTI(COMPGPU)

void init(void);
void loadContexts(void);
void startCompute(void);

END_ENGINE_NAMESPACE
