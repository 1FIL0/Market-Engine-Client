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

#include "compute_config.hpp"
#include "definitions.hpp"
#include "market_item.hpp"
#include "market_item_memory.hpp"
#include "namespace.hpp"
#include "randomiser.hpp"
#include "tradeup.hpp"
#include <algorithm>
#include <cstddef>
#include <cstdlib>
#include <emmintrin.h>
#include <vector>
#include <omp.h>
#include "cpu_operations.hpp"
#include <cmath>

USE_NAMESPACE_SHARE
USE_NAMESPACE_TRADEUP_ENGINE

void CPUOP::makeCombinationTradeup(TRADEUP::TradeupCPU &tradeupCPU, std::vector<ITEM::MarketItem> &combination)
{
    // ! MUST BE IN ORDER
    tradeupCPU.inputs = combination;
    CPUOP::pushAvgInputFloat(tradeupCPU);
    CPUOP::pushNormalizedAvgInputFloat(tradeupCPU);
    CPUOP::pushInputsCombinedPrice(tradeupCPU);
    CPUOP::pushOutputItems(tradeupCPU);
    CPUOP::pushChanceToProfit(tradeupCPU);
    CPUOP::pushProfitability(tradeupCPU);
}

uint64_t CPUOP::getCombinationsAmount(int n, int k) {
    if (k > n) return 0;
    if (k == 0 || k == n) return 1;

    long long result = 1;
    if (k > n - k) k = n - k;

    for (int i = 0; i < k; i++) {
        result *= (n - i);
        result /= (i + 1);
    }
    return result;
}


ITEM::MarketItem CPUOP::getRandomItem(const int grade, const int category, const int forceIndex)
{
    ITEM::MarketItem item;
    const std::vector<ITEM::MarketItem> &tradeCategoryGradeItemsRef = ITEM::getItemsTradeupableCategoryGrade(ITEM::TRADEUPABLE_TRUE, category, grade);

    if (forceIndex != -1) {item = tradeCategoryGradeItemsRef[forceIndex];}
    else {item = tradeCategoryGradeItemsRef[RAND::getRandomInt(0, tradeCategoryGradeItemsRef.size()-1)];}
    return item;
}

void CPUOP::pushRandomItemBatch(std::vector<ITEM::MarketItem> &batch, const size_t batchSize, 
                                const int grade, const int category, const float maxItemPrice)
{
    for (size_t i = 0; i < batchSize; ++i) {
        ITEM::MarketItem randItem;
        while (1) {
            randItem = getRandomItem(grade, category);
            if (randItem.price <= maxItemPrice) {break;}
        }
        batch[i] = randItem;
    }
    setBatchFloats(batch);
}

void CPUOP::pushSingleItemBatch(std::vector<ITEM::MarketItem> &batch, const size_t batchSize,
                                const int grade, const int category, const float maxItemPrice)
{
    int forcedIndex = 0;
    const std::vector<ITEM::MarketItem> &tradeCategoryGradeItemsRef = ITEM::getItemsTradeupableCategoryGrade(ITEM::TRADEUPABLE_TRUE, category, grade);
    size_t itemsSize = tradeCategoryGradeItemsRef.size();

    while (1) {
        forcedIndex = RAND::getRandomInt(0, itemsSize-1);
        if (tradeCategoryGradeItemsRef[forcedIndex].price <= maxItemPrice) {break;}
    }

    for (size_t i = 0; i < batchSize; ++i) {
        batch[i] = getRandomItem(grade, category, forcedIndex);
    }
    setBatchFloats(batch);
}

void CPUOP::setBatchFloats(std::vector<ITEM::MarketItem> &batch)
{
    for (auto &input : batch) {
        float wearMinFloat = DEFINITIONS::wearToMinFloat(input.wear);
        float wearMaxFloat = DEFINITIONS::wearToMaxFloat(input.wear);
        if (input.minFloat > wearMinFloat) {wearMinFloat = input.minFloat;}
        if (input.maxFloat < wearMaxFloat) {wearMaxFloat = input.maxFloat;}
        float finalMinFloat = std::lerp(wearMinFloat, wearMaxFloat, COMP::computeConfig.minimumInputFloatPercentage / 100.0);
        float finalMaxFloat = std::lerp(wearMinFloat, wearMaxFloat, COMP::computeConfig.maximumInputFloatPercentage / 100.0);
        input.floatVal = RAND::getRandomFloat(finalMinFloat, finalMaxFloat);
        pushNormalizedFloat(input, input.floatVal);
    }
}

void CPUOP::pushNormalizedFloat(ITEM::MarketItem &item, const float itemFloatVal)
{
    // avoid dividing by zero on vanilla knife skins that have -1 float ranges and floats
    float denom = item.maxFloat - item.minFloat;
    denom = (denom == 0.0) ? std::numeric_limits<float>::epsilon() : denom;
    item.normalizedFloatVal = (itemFloatVal - item.minFloat) / denom;
}

void CPUOP::pushAvgInputFloat(TRADEUP::TradeupCPU &tradeupCPU)
{
    float avgFloat = 0.0;
    for (auto &input : tradeupCPU.inputs) {
        avgFloat += input.floatVal;
    }
    avgFloat /= tradeupCPU.inputs.size();
    tradeupCPU.avgInputFloat = avgFloat;
}

void CPUOP::pushNormalizedAvgInputFloat(TRADEUP::TradeupCPU &tradeupCPU)
{
    float normalizedAvgFloat = 0.0;
    for (auto &input : tradeupCPU.inputs) {
        normalizedAvgFloat += input.normalizedFloatVal;
    }
    normalizedAvgFloat /= tradeupCPU.inputs.size();
    tradeupCPU.normalizedAvgInputFloat = normalizedAvgFloat;
}

void CPUOP::pushInputsCombinedPrice(TRADEUP::TradeupCPU &tradeupCPU)
{
    float totalPrice = 0.0;
    for (auto &item : tradeupCPU.inputs) {
        totalPrice += item.price;
    }
    tradeupCPU.totalInputPrice = totalPrice;
}

// THE PROBLEMATIC FUNCTION THAT FUCKS UP PERFORMANCE
void CPUOP::pushOutputItems(TRADEUP::TradeupCPU &tradeupCPU)
{
    std::vector<ITEM::MarketItem> outputs;
    std::array<float, DEFINITIONS::COLLECTION_END> collectionChances{};
    std::array<int, DEFINITIONS::COLLECTION_END> distinctCollectionItems{};

    for (auto &input : tradeupCPU.inputs) {
        collectionChances[input.collection] += (100.0 / tradeupCPU.inputs.size());
        
        for (auto oid = 0; oid < input.outputTempAccessIDSSize; ++oid) {
            ITEM::TempAccessID lowestWearOutputID = input.outputTempAccessIDS[oid];
            const auto &lowestWearOutput = ITEM::getItem(lowestWearOutputID);
            float outputFloat = calculateOutputItemFloat(lowestWearOutput.minFloat, lowestWearOutput.maxFloat, tradeupCPU.normalizedAvgInputFloat);
            int wear = DEFINITIONS::itemFloatValToInt(outputFloat);
            ITEM::MarketItem realOutput = ITEM::getItem(lowestWearOutputID + wear);
            realOutput.floatVal = outputFloat;
            pushNormalizedFloat(realOutput, realOutput.floatVal);
            
            // no duplicates allowed
            if (std::find(outputs.begin(), outputs.end(), realOutput) != outputs.end()) {
                continue;
            }

            outputs.push_back(realOutput);
            for (int oci = 0; oci < realOutput.outcomeCollectionsSize; ++oci) {
                ++distinctCollectionItems[realOutput.outcomeCollections[oci]];
            }
        }
    }

    // Makes no sense - change later
    for (auto &output : outputs) {
        for (int oci = 0; oci < output.outcomeCollectionsSize; ++oci) {
            int outcomeCollection = output.outcomeCollections[oci];
            output.tradeUpChance = collectionChances[outcomeCollection] / (1 * distinctCollectionItems[outcomeCollection]);
        }
    }

    tradeupCPU.outputs = outputs;
}

float CPUOP::calculateOutputItemFloat(const float outputMinFloat, const float outputMaxFloat, const float normalizedAvgInputFloat)
{
    float outputFloat = (outputMaxFloat - outputMinFloat) * normalizedAvgInputFloat + outputMinFloat;
    return outputFloat;
}

float CPUOP::getExpectedPrice(const std::vector<ITEM::MarketItem> &sortedOutputs)
{
    float expectedPrice = 0.0;

    for (auto &output : sortedOutputs) {
        expectedPrice += (output.tradeUpChance / 100) * output.price;
    }
    return expectedPrice;
}

float CPUOP::getExpectedPriceSteamTax(const std::vector<ITEM::MarketItem> &sortedOutputs)
{
    float expectedPrice = 0.0;

    for (auto &output : sortedOutputs) {
        expectedPrice += (output.tradeUpChance / 100) * output.priceSteamTax;
    }
    return expectedPrice;
}

void CPUOP::pushChanceToProfit(TRADEUP::TradeupCPU &tradeupCPU)
{
    float chanceToProfit = 0.0;
    for (auto &output : tradeupCPU.outputs) {
        if (output.price > tradeupCPU.totalInputPrice) {chanceToProfit += output.tradeUpChance;}
    }

    tradeupCPU.chanceToProfit = chanceToProfit;
}

void CPUOP::pushProfitability(TRADEUP::TradeupCPU &tradeupCPU)
{
    float profitability = (getExpectedPrice(tradeupCPU.outputs) / tradeupCPU.totalInputPrice) * 100;
    float profitabilitySteamTax = (getExpectedPriceSteamTax(tradeupCPU.outputs) / tradeupCPU.totalInputPrice) * 100;
    tradeupCPU.profitability = profitability;
    tradeupCPU.profitabilitySteamTax = profitabilitySteamTax;
}
