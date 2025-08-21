#pragma once

#include "market_item.cl"
#include "definitions.cl"
#include "tradeup.cl"

// NOT IN USE - RANDOMISING FLOATS DURING BATCH CREATION
//void pushInputFloatVals(__private Tradeup *tradeup)
//{
//    for (int i = 0; i < MAX_GPU_TRADEUP_INPUTS; ++i) {
//        float maxFloat = wearToMaxFloat(tradeup->inputs[i].wear);
//        float minFloat = wearToMinFloat(tradeup->inputs[i].wear);
//        if (tradeup->inputs[i].minFloat > minFloat && minFloat == FLOAT_MIN_FACTORY_NEW) {minFloat = tradeup->inputs[i].minFloat;}
//        if (tradeup->inputs[i].maxFloat < maxFloat && maxFloat == FLOAT_MAX_BATTLE_SCARRED) {maxFloat = tradeup->inputs[i].maxFloat;}
//        tradeup->inputs[i].floatVal = (minFloat + maxFloat) / 2.0;
//    }
//}

void pushTotalInputPrice(__private Tradeup *tradeup)
{
    float totalPrice = 0.0;
    for (int i = 0; i < MAX_GPU_TRADEUP_INPUTS; ++i) {
        totalPrice += tradeup->inputs[i].price;
        tradeup->totalInputPrice = totalPrice;
    }
}

void pushAvgInputFloat(__private Tradeup *tradeup)
{
    float avgFloat = 0.0;
    for (int i = 0; i < 10; ++i) {
        avgFloat += tradeup->inputs[i].floatVal;
    }
    avgFloat /= 10.0;
    tradeup->avgInputFloat = avgFloat;
}

float calculateOutputItemFloat(__private const MarketItem *outputItem, 
                                __private float avgFloat)
{
    return ((outputItem->maxFloat - outputItem->minFloat) * avgFloat + outputItem->minFloat);
}

void sortOutputItemsTickets(__private MarketItem *outputTickets,
                            __private int outputTicketsSize,
                            __private MarketItem *sortedOutputs,
                            __private int *sortedOutputsSize)
{
    __private MarketItem singleItems[256];
    __private int currentSingleItems = 0;
    __private int collectionAmounts[COLLECTION_END];

    // FOR REMOVE DUPLICATES AND ADD OUTPUT AMOUNTS TO COLLECTION ARRAY AND MARKET ITEMS
    for (int i = 0; i < outputTicketsSize; ++i) {
        bool dup = false;
        for (int j = 0; j < currentSingleItems; ++j) {
            if (singleItems[j].tempID == outputTickets[i].tempID) {
                ++singleItems[j].outputAmount;
                ++collectionAmounts[singleItems[j].collection];
                dup = true;
                break;
            }
        }

        if (dup) {
            continue;
        }
        
        singleItems[currentSingleItems] = outputTickets[i];
        singleItems[currentSingleItems].outputAmount = 1;
        ++collectionAmounts[outputTickets[i].collection];
        ++currentSingleItems;
    }

    // FOR CALCULATE TRADEUP CHANCE
    for (int i = 0; i < currentSingleItems; ++i) {
        int totalCollectionOutputs = collectionAmounts[singleItems[i].collection];
        singleItems[i].tradeUpChance = (((float)totalCollectionOutputs / outputTicketsSize) * singleItems[i].outputAmount / totalCollectionOutputs) * 100;
    }

    // FOR GET BACK MEMORY
    for (int i = 0; i < currentSingleItems; ++i) {
        sortedOutputs[i] = singleItems[i];
    }
    *sortedOutputsSize = currentSingleItems;
}

void pushOutputs(__private Tradeup *tradeup,
                __global MarketItem *outputItemsPool,
                __global int *collectionIndicesStart,
                __global int *collectionIndiciesEnd)
{
    __private int currentTicket = 0;
    __private MarketItem outputTickets[MAX_GPU_TRADEUP_OUTPUTS];

    for (int i = 0; i < 10; ++i) {
        int collectionIndexStart = collectionIndicesStart[tradeup->inputs[i].collection];
        int collectionIndexEnd = collectionIndiciesEnd[tradeup->inputs[i].collection];

        for (int j = collectionIndexStart; j < collectionIndexEnd; ++j) {
            MarketItem itemTicket = outputItemsPool[j];
            float itemFloatVal = calculateOutputItemFloat(&itemTicket, tradeup->avgInputFloat);

            if (itemTicket.wear != itemFloatValToInt(itemFloatVal)) {
                continue;
            }

            itemTicket.floatVal = itemFloatVal;
            outputTickets[currentTicket++] = itemTicket;
        }
    }

    __private int outputSize = currentTicket;
    __private int sortedOutputsSize;
    sortOutputItemsTickets(outputTickets, outputSize, tradeup->outputs, &sortedOutputsSize);
    tradeup->totalOutputSize = sortedOutputsSize;
}

float getExpectedPrice(__private Tradeup *tradeup)
{
    float expectedPrice = 0.0;

    for (int i = 0; i < tradeup->totalOutputSize; ++i) {
        expectedPrice += (tradeup->outputs[i].tradeUpChance / 100.0) * tradeup->outputs[i].price;
    }
    return expectedPrice;
}

void pushProfitability(__private Tradeup *tradeup)
{
    float expectedPrice = getExpectedPrice(tradeup);
    float profitability = (expectedPrice / tradeup->totalInputPrice) * 100;
    float profitabilitySteamTax = ((expectedPrice * 0.85) / tradeup->totalInputPrice) * 100;
    tradeup->profitability = profitability;
    tradeup->profitabilitySteamTax = profitabilitySteamTax;
}

void pushChanceToProfit(__private Tradeup *tradeup)
{
    float chanceToProfit = 0.0;
    float chanceToProfitSteamTax = 0.0;
    for (int i = 0; i < tradeup->totalOutputSize; ++i) {
        if (tradeup->outputs[i].price > tradeup->totalInputPrice) {
            chanceToProfit += tradeup->outputs[i].tradeUpChance;
        }
        if (tradeup->outputs[i].priceSteamTax > tradeup->totalInputPrice) {
            chanceToProfitSteamTax += tradeup->outputs[i].tradeUpChance;
        }
    }

    tradeup->chanceToProfit = chanceToProfit;
    tradeup->chanceToProfitSteamTax = chanceToProfitSteamTax;
}
