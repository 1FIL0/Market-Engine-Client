#include "definitions.hpp"
#include "market_item.hpp"
#include "market_item_memory.hpp"
#include "namespace.hpp"
#include "randomiser.hpp"
#include "tradeup.hpp"
#include <cstddef>
#include <cstdlib>
#include <emmintrin.h>
#include <vector>
#include <omp.h>
#include "cpu_operations.hpp"

USE_NAMESPACE_SHARE
USE_NAMESPACE_TRADEUP_ENGINE

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
        float finalMinFloat = wearMinFloat;
        float finalMaxFloat = wearMaxFloat;
        if (input.minFloat > wearMinFloat) {finalMinFloat = input.minFloat;}
        if (input.maxFloat < wearMaxFloat) {finalMaxFloat = input.maxFloat;}
        input.floatVal = RAND::getRandomFloat(finalMinFloat, finalMaxFloat);
    }
}

// NOT IN USE - SETTING FLOATS DURING BATCH PRODUCTION
//void CPUOP::pushInputFloats(TRADEUP::TradeupCPU &tradeupCPU)
//{
//    for (auto &input : tradeupCPU.inputs) {
//        float maxFloat = DEFINITIONS::wearToMaxFloat(input.wear);
//        float minFloat = DEFINITIONS::wearToMinFloat(input.wear);
//        if (input.minFloat > minFloat && minFloat == DEFINITIONS::FLOAT_MIN_FACTORY_NEW) {minFloat = input.minFloat;}
//        if (input.maxFloat < maxFloat && maxFloat == DEFINITIONS::FLOAT_MAX_BATTLE_SCARRED) {maxFloat = input.maxFloat;}
//        input.floatVal = (minFloat + maxFloat) / 2.0;
//    }
//}

void CPUOP::pushAvgInputFloat(TRADEUP::TradeupCPU &tradeupCPU)
{
    float avgFloat = 0.0;
    for (auto &input : tradeupCPU.inputs) {
        avgFloat += input.floatVal;
    }
    avgFloat /= 10.0;
    tradeupCPU.avgInputFloat = avgFloat;
}

void CPUOP::pushInputsCombinedPrice(TRADEUP::TradeupCPU &tradeupCPU)
{
    float totalPrice = 0.0;
    for (auto &item : tradeupCPU.inputs) {
        totalPrice += item.price;
    }
    tradeupCPU.totalInputPrice = totalPrice;
}

void CPUOP::pushOutputItems(TRADEUP::TradeupCPU &tradeupCPU)
{
    std::vector<ITEM::MarketItem> outputs;

    for (auto &input : tradeupCPU.inputs) {
        const std::vector<ITEM::MarketItem> &collectionItemsRef = ITEM::getItemsCategoryGradeCollection(input.category, input.grade + 1, input.collection);
        std::vector<ITEM::MarketItem> collectionItemsCopy = collectionItemsRef;

        for (auto &collectionItemCopy : collectionItemsCopy) {
            float floatVal = calculateOutputItemFloat(collectionItemCopy, tradeupCPU.avgInputFloat);
            if (DEFINITIONS::itemFloatValToInt(floatVal) != collectionItemCopy.wear) {continue;}
            collectionItemCopy.floatVal = floatVal;
            outputs.push_back(collectionItemCopy);
        }
    }

    std::vector<ITEM::MarketItem> sortedOutputs = sortOutputTickets(outputs);
    tradeupCPU.outputs = sortedOutputs;
}

float CPUOP::calculateOutputItemFloat(const ITEM::MarketItem &outputItem, const float avgFloat)
{
    return ((outputItem.maxFloat - outputItem.minFloat) * avgFloat + outputItem.minFloat);
}

std::vector<ITEM::MarketItem> CPUOP::sortOutputTickets(std::vector<ITEM::MarketItem> &outputs)
{
    std::vector<ITEM::MarketItem> sortedOutputs;
    std::vector<ITEM::MarketItem> singleItems;
    std::array<int, DEFINITIONS::COLLECTION_END> collectionAmounts;
    size_t outputsSize = outputs.size();

    // FOR REMOVE DUPLICATES AND ADD OUTPUT AMOUNTS TO COLLECTION ARRAY AND MARKET ITEMS
    for (auto &output : outputs) {
        bool dup = false;
        for (auto &singleItem : singleItems) {
            if (singleItem.tempID == output.tempID) {
                ++singleItem.outputAmount;
                ++collectionAmounts[singleItem.collection];
                dup = true;
                break;
            }
        }

        if (dup) {
            continue;
        }
        
        output.outputAmount = 1;
        singleItems.push_back(output);
        ++collectionAmounts[output.collection];
    }

    // FOR CALCULATE TRADEUP CHANCE
    for (auto &singleItem : singleItems) {
        int totalCollectionOutputs = collectionAmounts[singleItem.collection];
        singleItem.tradeUpChance = (((float)totalCollectionOutputs / outputsSize) * singleItem.outputAmount / totalCollectionOutputs) * 100;
    }

    // FOR GET BACK MEMORY
    for (auto &singleItem : singleItems) {
        sortedOutputs.push_back(singleItem);
    }

    return sortedOutputs;
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
