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

#include "definitions.cl"
#include "market_item.cl"
#include "definitions.cl"
#include "tradeup.cl"

void pushNormalizedFloat(__private MarketItem *item, __private const float itemFloatVal)
{
    float denom = item->maxFloat - item->minFloat;
    denom = (denom == 0.0f) ? FLT_EPSILON : denom;
    item->normalizedFloatVal = (itemFloatVal - item->minFloat) / denom;
}

void pushTotalInputPrice(__global TradeupGPU *tradeup)
{
    float totalPrice = 0.0;
    for (int i = 0; i < tradeup->totalInputSize; ++i) {
        totalPrice += tradeup->inputs[i].price;
        tradeup->totalInputPrice = totalPrice;
    }
}

void pushAvgInputFloat(__global TradeupGPU *tradeup)
{
    float avgFloat = 0.0;
    for (int i = 0; i < tradeup->totalInputSize; ++i) {
        avgFloat += tradeup->inputs[i].floatVal;
    }
    avgFloat /= tradeup->totalInputSize;
    tradeup->avgInputFloat = avgFloat;
}

void pushNormalizedAvgInputFloat(__global TradeupGPU *tradeup)
{
    float normalizedAvgFloat = 0.0;
    for (int i = 0; i < tradeup->totalInputSize; ++i) {
        normalizedAvgFloat += tradeup->inputs[i].normalizedFloatVal;
    }
    normalizedAvgFloat /= tradeup->totalInputSize;
    tradeup->normalizedAvgInputFloat = normalizedAvgFloat;
}

float calculateOutputItemFloat(__private const float minFloat,
                                __private const float maxFloat, 
                                __private const float avgFloat)
{
    return ((maxFloat - minFloat) * avgFloat + minFloat);
}

// THE PROBLEMATIC FUNCTION THAT FUCKS UP PERFORMANCE
void pushOutputItems(__global TradeupGPU *tradeup,
                    __global float *minFloats,
                    __global float *maxFloats,

                    __global int *flatOutcomeCollections,
                    __global int *flatOutcomeCollectionsIndicesStart,
                    __global int *flatOutcomeCollectionsIndicesEnd,

                    __global int *flatOutputIds,
                    __global int *flatOutputIdsIndicesStart,
                    __global int *flatOutputIdsIndicesEnd
                )
{
    __private float collectionChances[COLLECTION_END] = {0.0};
    __private int distinctCollectionItems[COLLECTION_END] = {0};
    __private int currentOutputItem = 0;

    for (int i = 0; i < tradeup->totalInputSize; ++i) {
        MarketItem input = tradeup->inputs[i];
        collectionChances[input.collection] += (100.0 / tradeup->totalInputSize); 

        for (int oidx = flatOutputIdsIndicesStart[input.tempAccessID]; oidx < flatOutputIdsIndicesEnd[input.tempAccessID]; ++oidx) {
            int lowestWearOutputID = flatOutputIds[oidx];
            float outputFloat = calculateOutputItemFloat(minFloats[lowestWearOutputID], maxFloats[lowestWearOutputID], tradeup->normalizedAvgInputFloat);
            int outputWear = itemFloatValToInt(outputFloat);
            int realOutputID = flatOutputIds[lowestWearOutputID + outputWear];
            
            int v = realOutputID;

            int found = 0;
            for (int j = 0; j < tradeup->totalOutputSize; j++) {
                found |= (tradeup->outputTempIDS[j] == v);
            }
            int isNew = 1 - found;
            tradeup->outputTempIDS[tradeup->totalOutputSize] = v * isNew + tradeup->outputTempIDS[tradeup->totalOutputSize] * (1 - isNew);
            tradeup->outputFloats[tradeup->totalOutputSize] = outputFloat * isNew + tradeup->outputFloats[tradeup->totalOutputSize] * (1 - isNew);
            tradeup->outputWears[tradeup->totalOutputSize] = outputWear * isNew + tradeup->outputFloats[tradeup->totalOutputSize] * (1 - isNew);
            
            for (int ocidx = flatOutcomeCollectionsIndicesStart[v]; ocidx < flatOutcomeCollectionsIndicesEnd[v]; ++ocidx) {
                int outcomeCollection = flatOutcomeCollections[ocidx];
                distinctCollectionItems[outcomeCollection] += isNew;
            }

            tradeup->totalOutputSize += isNew;
        }
    }

    for (int i = 0; i < tradeup->totalOutputSize; ++i) {
        int outputID = tradeup->outputTempIDS[i];
        int outcomeCollection = flatOutcomeCollections[flatOutcomeCollectionsIndicesStart[outputID]];
        tradeup->outputTradeupChances[i] = collectionChances[outcomeCollection] / (1 * distinctCollectionItems[outcomeCollection]);
    }

    tradeup->totalOutputSize = currentOutputItem;
}

float getExpectedPrice(__global TradeupGPU *tradeup, __global float *prices)
{
    float expectedPrice = 0.0;

    for (int i = 0; i < tradeup->totalOutputSize; ++i) {
        expectedPrice += (tradeup->outputTradeupChances[i] / 100.0) * prices[tradeup->outputTempIDS[i]];
    }
    return expectedPrice;
}

void pushProfitability(__global TradeupGPU *tradeup, __global float *prices)
{
    float expectedPrice = getExpectedPrice(tradeup, prices);
    float profitability = (expectedPrice / tradeup->totalInputPrice) * 100;
    float profitabilitySteamTax = ((expectedPrice * 0.85) / tradeup->totalInputPrice) * 100;
    tradeup->profitability = profitability;
    tradeup->profitabilitySteamTax = profitabilitySteamTax;
}

void pushChanceToProfit(__global TradeupGPU *tradeup, __global float *prices)
{
    float chanceToProfit = 0.0;
    for (int i = 0; i < tradeup->totalOutputSize; ++i) {
        if (prices[tradeup->outputTempIDS[i]] > tradeup->totalInputPrice) {
            chanceToProfit += tradeup->outputTradeupChances[i];
        }
    }

    tradeup->chanceToProfit = chanceToProfit;
    tradeup->chanceToProfitSteamTax = chanceToProfit;
}
