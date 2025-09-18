/*
* Market Engine Client
* Copyright (C) 2025 OneFil (1FIL0) https://github.com/1FIL0
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/


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

