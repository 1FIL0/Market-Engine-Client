#include "compute_config.hpp"
#include "gpu_compute.hpp"
#include "cpu_compute.hpp"
#include "randomiser.hpp"
#include "market_item_memory.hpp"
#include "tradeup_handler.hpp"

USE_NAMESPACE_SHARE
USE_NAMESPACE_TRADEUP_ENGINE

int main(void)
{
    std::setlocale(LC_NUMERIC, "en_US.UTF-8");
    ITEM::loadEverything();
    RAND::init();
    TRADEUP::initTradeupHandler();

    if (COMP::computeConfig.computeMode == COMP::COMPUTE_MODE_CPU) {
        COMPCPU::init();
        COMPCPU::startCompute();
    }
    else {
        COMPGPU::init();
        COMPGPU::startCompute();
    }

    return 0;
}