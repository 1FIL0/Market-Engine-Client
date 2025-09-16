#include "gpu_compute_context.hpp"
#include "compute_config.hpp"
#include "definitions.hpp"
#include "gpu_compute_error.hpp"
#include "logger.hpp"
#include "market_item.hpp"
#include "market_item_memory.hpp"
#include <CL/cl.h>
#include <CL/cl_platform.h>
#include <CL/opencl.hpp>
#include <cstdint>
#include <rapidjson/document.h>
#include <rapidjson/prettywriter.h>
#include <rapidjson/stringbuffer.h>
#include <string>
#include <vector>
#include "cpu_operations.hpp"
#include "definitions.hpp"
#include "time.hpp"
#include "tradeup.hpp"
#include "tradeup_handler.hpp"
#include "tradeup_hardware_converter.hpp"
#include "kernel_cl_embedded.hpp"
#include "system_info.hpp"
#include <iostream>

USE_NAMESPACE_TRADEUP_ENGINE
USE_NAMESPACE_SHARE

COMPGPU::ComputeContext::ComputeContext(const cl::Device &a_device, const bool debug)
{
    m_debugMode = debug;

    m_device = a_device;
    m_platform = m_device.getInfo<CL_DEVICE_PLATFORM>();
    m_context = cl::Context(m_device);
    m_queue = cl::CommandQueue(m_context, m_device);

    m_platformName = m_platform.getInfo<CL_PLATFORM_NAME>();
    m_platformVendor = m_platform.getInfo<CL_PLATFORM_VENDOR>();
    m_deviceName = m_device.getInfo<CL_DEVICE_NAME>();
    m_computeUnits = m_device.getInfo<CL_DEVICE_MAX_COMPUTE_UNITS>();
    m_memorySize = m_device.getInfo<CL_DEVICE_GLOBAL_MEM_SIZE>();

    sendInfo();
    buildKernel();
    initData();
    createStaticBuffers();
}

void COMPGPU::ComputeContext::buildKernel(void)
{
    try {
        LOGGER::sendMessage("Building Program");
        LOGGER::sendMessage(DIR_MARKET_ENGINE_GPU_KERNEL_PATH);
        std::string fullSource = "";
        fullSource += std::string(reinterpret_cast<const char *>(kernel_cl_hpp_kernel), kernel_cl_hpp_kernel_len);
        m_program = cl::Program(m_context, fullSource);
        std::string options = "-cl-fast-relaxed-math -cl-mad-enable -cl-single-precision-constant -cl-denorms-are-zero";
        m_program.build(options.c_str());
        m_kernel = cl::Kernel(m_program, "combinationKernel");
    }
    catch (cl::Error &err) {
        LOGGER::sendMessage(getCLError(err));
        std::string buildLog = m_program.getBuildInfo<CL_PROGRAM_BUILD_LOG>(m_device);
        LOGGER::sendMessage("Build Log: " + buildLog);
    }
}

void COMPGPU::ComputeContext::sendInfo(void)
{
    std::string diag = "";
    diag += "Compute Context Info";
    diag += "\n[Using Platform] " + m_platformName + " / " + m_platformVendor;
    diag += "\n[Using Device] " + m_deviceName; 
    diag += "\n[Compute Units] " + std::to_string(m_computeUnits);
    diag += "\n[Max Global Memory] " + std::to_string((m_memorySize / 1024) / 1024) + "MB";
    diag += "\n[Debug]: " + std::to_string(m_debugMode);
    diag += "\n";
    LOGGER::sendMessage(diag);
}

void COMPGPU::ComputeContext::logComputeDiagnostics(const int category, const int grade, const uint64_t currentBatch)
{
    std::string msg = "Processing Combinations \n[Category = " + std::to_string(category) + 
                        "] \n[Grade = " + std::to_string(grade) +  "] \n[Combinations = " + std::to_string(m_combinationsAmount) + "] ";
    msg += "\n[Current Batch = " + std::to_string(currentBatch) + "]";
    msg += "\n[Batch Size = " + std::to_string(m_batch.size()) + "] ";
    msg += "\n[Batch = ";
    for (auto &item : m_batch) {
        auto coldData = ITEM::getColdData(item);
        msg += coldData.weaponName + " " + coldData.skinName + ", ";
    }
    for (int i = 0; i < 2; ++i)
        msg.pop_back();
    msg += "]\n";
    LOGGER::sendMessage(msg);
}

void COMPGPU::ComputeContext::initData(void)
{
    SYSTEM::SystemInfoBlock systemInfo = SYSTEM::getSystemInfo();

    if (COMP::computeConfig.outputVerbose) LOGGER::sendMessage("Initializing data");
    m_combinationsAmount = CPUOP::getCombinationsAmount(COMP::computeConfig.batchSize, 10);
    m_tradeupsSize = m_combinationsAmount;
    if (systemInfo.freeRamBytes <= sizeof(TRADEUP::TradeupGPU) * m_tradeupsSize) {
        LOGGER::sendMessage("Out of memory! Try Lowering the batch amount");
        exit(-1);
    }
    m_tradeupsGPU.resize(m_combinationsAmount);
    m_batch.resize(COMP::computeConfig.batchSize);
    m_profitabilityMargin = COMP::computeConfig.profitMargin;
}

void COMPGPU::ComputeContext::createStaticBuffers(void)
{
    if (COMP::computeConfig.outputVerbose) LOGGER::sendMessage("Creating Static Buffers");
    m_tradeupsBuffer = cl::Buffer(m_context, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR,
                                    sizeof(TRADEUP::TradeupGPU) * m_tradeupsGPU.size(), m_tradeupsGPU.data());
    m_batchBuffer = cl::Buffer(m_context, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, sizeof(ITEM::MarketItem) * m_batch.size(), m_batch.data());
}

void COMPGPU::ComputeContext::prepareBatch(const int category, const int grade)
{
    if (COMP::computeConfig.outputVerbose) LOGGER::sendMessage("Preparing Batch [" + std::to_string(m_batch.size()) + "]");
    (COMP::computeConfig.singleItem) ? CPUOP::pushSingleItemBatch(m_batch, COMP::computeConfig.batchSize, grade, category, COMP::computeConfig.maxInputPrice) :
                                    CPUOP::pushRandomItemBatch(m_batch, COMP::computeConfig.batchSize, grade, category, COMP::computeConfig.maxInputPrice);
}

void COMPGPU::ComputeContext::prepareBuffers(const int category, const int grade)
{
    cleanTradeups();
    prepareBatch(category, grade);

    // Create entirely new buffers - REDO THIS LATER TO IMPROVE PERFORMANCE
    if (COMP::computeConfig.outputVerbose) LOGGER::sendMessage("Preparing buffers");
    ITEM::MarketItemMemoryFlatCollections collectionOutputsFlat = ITEM::getItemsTradeupableCategoryGradeCollectionsFlattened(category, grade + 1);
    
    m_flatCollectionOutputsBuffer = cl::Buffer(m_context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 
                                                sizeof(ITEM::MarketItem) * collectionOutputsFlat.collectionItemsFlat.size(), collectionOutputsFlat.collectionItemsFlat.data());
    m_collectionIndicesStartBuffer = cl::Buffer(m_context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 
                                            sizeof(int) * collectionOutputsFlat.collectionsIndicesStart.size(), collectionOutputsFlat.collectionsIndicesStart.data());
    m_collectionIndicesEndBuffer = cl::Buffer(m_context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 
                                                sizeof(int) * collectionOutputsFlat.collectionsIndicesEnd.size(), collectionOutputsFlat.collectionsIndicesEnd.data());
    
    // Modify the static buffers
    size_t tradeupsDataSize = sizeof(TRADEUP::TradeupGPU) * m_tradeupsGPU.size();
    TRADEUP::TradeupGPU *tradeupsMappedPtr = (TRADEUP::TradeupGPU *)m_queue.enqueueMapBuffer(m_tradeupsBuffer, CL_TRUE, CL_MAP_WRITE, 0, tradeupsDataSize);
    std::memcpy(tradeupsMappedPtr, m_tradeupsGPU.data(), tradeupsDataSize);
    m_queue.enqueueUnmapMemObject(m_tradeupsBuffer, tradeupsMappedPtr);
    
    size_t batchDataSize = sizeof(ITEM::MarketItem) * m_batch.size();
    ITEM::MarketItem *batchMappedPtr = (ITEM::MarketItem *)m_queue.enqueueMapBuffer(m_batchBuffer, CL_TRUE, CL_MAP_WRITE, 0, batchDataSize);
    std::memcpy(batchMappedPtr, m_batch.data(), batchDataSize);
    m_queue.enqueueUnmapMemObject(m_batchBuffer, batchMappedPtr);
}

void COMPGPU::ComputeContext::cleanTradeups(void)
{
    if (m_debugMode) {
        m_tradeupsGPU.clear();
        m_tradeupsGPU.resize(m_tradeupsSize);
        return;
    }

    // RISKY - Not clearing and resizing tradeups vector. It will be hard to find if this bugs out in some way. 
    // the point of this is to not waste a massive amount of time on resizing the vector. i trust in the gpu kernel
    // to replace old values with its own tradeup and for it and to not bug out because of old values. 
    // I also trust in the host code to not bug out either.
    
    for (auto &tradeup : m_tradeupsGPU) {
        tradeup.processed = false;
    }
}

void COMPGPU::ComputeContext::setKernelArgs(void)
{
    if (COMP::computeConfig.outputVerbose) LOGGER::sendMessage("Setting kernel args");
    uint32_t batchSize = (uint32_t)m_batch.size();
    m_kernel.setArg(0, sizeof(cl_mem), &m_tradeupsBuffer);
    m_kernel.setArg(1, sizeof(cl_mem), &m_batchBuffer);
    m_kernel.setArg(2, sizeof(cl_mem), &m_flatCollectionOutputsBuffer);
    m_kernel.setArg(3, sizeof(cl_mem), &m_collectionIndicesStartBuffer);
    m_kernel.setArg(4, sizeof(cl_mem), &m_collectionIndicesEndBuffer); 
    m_kernel.setArg(5, sizeof(uint32_t), &batchSize);
    m_kernel.setArg(6, sizeof(uint64_t), &m_combinationsAmount);
    m_kernel.setArg(7, sizeof(float), &m_profitabilityMargin);
}

void COMPGPU::ComputeContext::startCompute(void)
{
    uint64_t currentBatch = 0;

    for (;;)
    for (auto &category : COMP::computeConfig.categories)
    for (auto &grade : COMP::computeConfig.grades) {
        if (category == DEFINITIONS::CATEGORY_STAT_TRAK && grade < DEFINITIONS::GRADE_MILSPEC) {
            continue;
        }

        prepareBuffers(category, grade);
        setKernelArgs();

        if (COMP::computeConfig.outputVerbose) logComputeDiagnostics(category, grade, currentBatch);

        execKernel();
        processTradeups();
        ++currentBatch;

        // Only one batch 4 debug
        if (m_debugMode) {
            return;
        }
    }
}

void COMPGPU::ComputeContext::execKernel(void)
{
    if (COMP::computeConfig.outputVerbose) LOGGER::sendMessage("Executing Kernel");
    cl::NDRange global = (m_debugMode) ? cl::NDRange(1) : cl::NDRange(m_combinationsAmount);
    m_queue.enqueueNDRangeKernel(m_kernel, cl::NullRange, global);

    m_queue.finish();
    m_queue.enqueueReadBuffer(m_tradeupsBuffer, CL_TRUE, 0, sizeof(TRADEUP::TradeupGPU) * m_tradeupsSize, m_tradeupsGPU.data());
}

void COMPGPU::ComputeContext::processTradeups(void)
{
    if (COMP::computeConfig.outputVerbose) LOGGER::sendMessage("Processing tradeups");
    for (auto &tradeupGPU : m_tradeupsGPU) {
        if (!tradeupGPU.processed || tradeupGPU.profitability < COMP::computeConfig.profitMargin) {
            continue;
        }
        TRADEUP::TradeupCPU profitableTradeupCPU = TRADEUP::GPU2CPU(tradeupGPU);
        TRADEUP::writeTradeup(profitableTradeupCPU, m_deviceName);
    }
}