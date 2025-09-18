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
* See LICENCE file.
*/

#pragma once

#include "namespace.hpp"
#include "tradeup.hpp"

#define CL_TARGET_OPENCL_VERSION 300
#define CL_HPP_TARGET_OPENCL_VERSION 300
#define CL_HPP_ENABLE_EXCEPTIONS
#include <CL/opencl.hpp>

START_ENGINE_NAMESPACE_MULTI(COMPGPU)

class ComputeContext {
    private:
        bool m_debugMode;
        
        cl::Platform m_platform;
        cl::Context m_context;
        cl::Device m_device;
        cl::CommandQueue m_queue;
        cl::Kernel m_kernel;
        cl::Program m_program;

        std::string m_platformName;
        std::string m_platformVendor;
        std::string m_deviceName;
        cl_uint m_computeUnits;
        cl_uint m_memorySize;

        cl::Buffer m_tradeupsBuffer;
        cl::Buffer m_batchBuffer;
        cl::Buffer m_flatCollectionOutputsBuffer;
        cl::Buffer m_collectionIndicesStartBuffer;
        cl::Buffer m_collectionIndicesEndBuffer;

        uint64_t m_combinationsAmount;
        uint64_t m_tradeupsSize;
        float m_profitabilityMargin;

        std::vector<TRADEUP::TradeupGPU> m_tradeupsGPU;
        std::vector<ITEM::MarketItem> m_batch;

        void buildKernel(void);
        void logComputeDiagnostics(const int category, const int grade, const uint64_t currentBatch);
        void sendInfo(void);
        void initData(void);
        void createStaticBuffers(void);
        void prepareBatch(const int category, const int grade);
        void prepareBuffers(const int category, const int grade);
        void cleanTradeups(void);
        void setKernelArgs(void);
        void processTradeups(void);

    public:
        ComputeContext(const cl::Device &a_device, const bool debug = false);

        void startCompute(void);
        void execKernel(void);
};

END_ENGINE_NAMESPACE