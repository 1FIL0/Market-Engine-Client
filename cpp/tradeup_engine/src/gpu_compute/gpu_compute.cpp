#include "gpu_compute.hpp"
#include "compute_config.hpp"
#include "gpu_compute_error.hpp"
#include <CL/cl.h>
#include <CL/cl_platform.h>
#include <CL/opencl.hpp>
#include <climits>
#include <cstring>
#include <rapidjson/document.h>
#include <rapidjson/rapidjson.h>
#include <sys/types.h>
#include <thread>
#include <vector>
#include <rapidjson/prettywriter.h>
#include <rapidjson/stringbuffer.h>
#include "gpu_compute_context.hpp"
#include "logger.hpp"

USE_NAMESPACE_TRADEUP_ENGINE
USE_NAMESPACE_SHARE

std::vector<cl::Platform> g_platforms;
std::vector<COMPGPU::ComputeContext> g_computeContexts;
std::vector<std::thread> g_computeThreads;
bool g_debug = false;

void COMPGPU::init()
{
    loadContexts();
}

void COMPGPU::loadContexts(void)
{
    try {
        LOGGER::sendMessage("Getting platforms");
        cl::Platform::get(&g_platforms);

        for (auto &configDevice : COMP::computeConfig.devices)
        for (auto &platform : g_platforms) {
            std::vector<cl::Device> devices;
            std::string platformName = platform.getInfo<CL_PLATFORM_NAME>();
            LOGGER::sendMessage("Getting devices from " + platformName);
            platform.getDevices(CL_DEVICE_TYPE_GPU, &devices);

            // DEBUGGER
            if (platformName == "Oclgrind") {
                g_computeContexts.push_back(devices[0]);
                return;
            }

            for (auto &device : devices) {
                if (device.getInfo<CL_DEVICE_NAME>() == configDevice) {
                    g_computeContexts.push_back(ComputeContext(device, g_debug));
                }
            }
        }
    }
    catch (cl::Error &err) {
        LOGGER::sendMessage(getCLError(err));
    }
}

void COMPGPU::startCompute(void)
{
    for (auto &computeContext : g_computeContexts) {
        g_computeThreads.emplace_back(&ComputeContext::startCompute, &computeContext);
    }

    for (auto &thread : g_computeThreads) {
        thread.join();
    }
}

