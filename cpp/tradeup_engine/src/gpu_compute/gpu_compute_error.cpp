#include "gpu_compute_error.hpp"
#include <string>

USE_NAMESPACE_TRADEUP_ENGINE

std::string COMPGPU::getCLError(const cl::Error &error)
{
    return std::string("CL ERROR: " + std::string(error.what()) + " " + std::to_string(error.err()));
}
