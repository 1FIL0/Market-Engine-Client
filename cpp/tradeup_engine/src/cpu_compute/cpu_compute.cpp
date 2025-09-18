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
* read LICENCE file
*/

#include "cpu_compute.hpp"
#include "compute_config.hpp"
#include "cpu_operations.hpp"
#include "definitions.hpp"
#include "logger.hpp"
#include "market_item_memory.hpp"
#include <cstdint>
#include <rapidjson/document.h>
#include <rapidjson/prettywriter.h>
#include <rapidjson/stringbuffer.h>
#include "time.hpp"
#include <openssl/sha.h>
#include <string>
#include "hasher.hpp"
#include "tradeup_handler.hpp"
#include "tradeup.hpp"

USE_NAMESPACE_TRADEUP_ENGINE
USE_NAMESPACE_SHARE

void COMPCPU::init(void)
{
    
}

void COMPCPU::startCompute(void)
{
    uint64_t currentBatch = 0;
    int batchSize = COMP::computeConfig.batchSize;
    std::vector<ITEM::MarketItem> batch;
    batch.resize(batchSize);
    uint64_t combinationsAmount = CPUOP::getCombinationsAmount(COMP::computeConfig.batchSize, 10);

    for (;;)
    for (auto &category : COMP::computeConfig.categories)
    for (auto &grade : COMP::computeConfig.grades) {
        if (category == DEFINITIONS::CATEGORY_STAT_TRAK && grade < DEFINITIONS::GRADE_MILSPEC) {
            continue;
        }

        (COMP::computeConfig.singleItem) ? CPUOP::pushSingleItemBatch(batch, COMP::computeConfig.batchSize, grade, category, COMP::computeConfig.maxInputPrice) :
                                            CPUOP::pushRandomItemBatch(batch, COMP::computeConfig.batchSize, grade, category, COMP::computeConfig.maxInputPrice);

        if (COMP::computeConfig.outputVerbose) {
            logComputeDiagnostics(category, grade, batch, currentBatch, combinationsAmount);
        }
        
        processCombinations(batch, combinationsAmount);  

        ++currentBatch;
    }
}

void COMPCPU::logComputeDiagnostics(const int category, const int grade, const std::vector<ITEM::MarketItem> batch, const uint64_t currentBatch, const uint64_t combinationsAmount)
{
    std::string msg = "Processing Combinations \n[Category = " + std::to_string(category) + 
                        "] \n[Grade = " + std::to_string(grade) +  "] \n[Combinations = " + std::to_string(combinationsAmount) + "] ";
    msg += "\n[Current Batch = " + std::to_string(currentBatch) + "]";
    msg += "\n[Batch Size = " + std::to_string(batch.size()) + "] ";
    msg += "\n[Batch = ";
    for (auto &item : batch) {
        auto coldData = ITEM::getColdData(item);
        msg += coldData.weaponName + " " + coldData.skinName + ", ";
    }
    for (int i = 0; i < 2; ++i)
        msg.pop_back();
    msg += "]\n";
    LOGGER::sendMessage(msg);
}

void COMPCPU::processCombinations(const std::vector<ITEM::MarketItem> &batch, const uint64_t combinationsAmount)
{
    int n = batch.size();
    const int combSize = 10;

    #pragma omp parallel
    {
        #pragma omp for
        for (uint64_t combStart = 0; combStart < combinationsAmount; ++combStart) {
            int localIndices[combSize];
            int combTemp = combStart;
            for (int i = 0; i < combSize; ++i) {
                localIndices[i] = combTemp % (n - i) + i;
                combTemp /= (n - i);
            }
    
            std::vector<ITEM::MarketItem> combination(10);
            for (int i = 0; i < combSize; ++i) {
                combination[i] = batch[localIndices[i]];
            }
    
            yieldCombination(combination);
        }
    }
}

void COMPCPU::yieldCombination(const std::vector<ITEM::MarketItem> &combination)
{
    TRADEUP::TradeupCPU tradeupCPU;
    tradeupCPU.inputs = combination;
    
    CPUOP::pushAvgInputFloat(tradeupCPU);
    CPUOP::pushInputsCombinedPrice(tradeupCPU);
    CPUOP::pushOutputItems(tradeupCPU);
    CPUOP::pushChanceToProfit(tradeupCPU);
    CPUOP::pushProfitability(tradeupCPU);

    if (tradeupCPU.profitability >= COMP::computeConfig.profitMargin) {
        #pragma omp critical
        {
            saveTradeupToFile(tradeupCPU);
        }
    }
}

void COMPCPU::saveTradeupToFile(TRADEUP::TradeupCPU &tradeupCPU)
{
    TRADEUP::writeTradeup(tradeupCPU, "CPU");
}