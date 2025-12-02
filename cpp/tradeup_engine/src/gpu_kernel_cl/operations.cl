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

#include "market_item.cl"
#include "definitions.cl"
#include "tradeup.cl"

void pushNormalizedFloat(__private MarketItem *item, __private const float itemFloatVal)
{
    float denom = item->maxFloat - item->minFloat;
    denom = (denom == 0.0f) ? FLT_EPSILON : denom;
    item->normalizedFloatVal = (itemFloatVal - item->minFloat) / denom;
}

void pushTotalInputPrice(__private TradeupGPU *tradeup)
{
    float totalPrice = 0.0;
    for (int i = 0; i < tradeup->totalInputSize; ++i) {
        totalPrice += tradeup->inputs[i].price;
        tradeup->totalInputPrice = totalPrice;
    }
}

void pushAvgInputFloat(__private TradeupGPU *tradeup)
{
    float avgFloat = 0.0;
    for (int i = 0; i < tradeup->totalInputSize; ++i) {
        avgFloat += tradeup->inputs[i].floatVal;
    }
    avgFloat /= tradeup->totalInputSize;
    tradeup->avgInputFloat = avgFloat;
}

void pushNormalizedAvgInputFloat(__private TradeupGPU *tradeup)
{
    float normalizedAvgFloat = 0.0;
    for (int i = 0; i < tradeup->totalInputSize; ++i) {
        normalizedAvgFloat += tradeup->inputs[i].normalizedFloatVal;
    }
    normalizedAvgFloat /= tradeup->totalInputSize;
    tradeup->normalizedAvgInputFloat = normalizedAvgFloat;
}

float calculateOutputItemFloat(__private const MarketItem *outputItem, 
                                __private float avgFloat)
{
    return ((outputItem->maxFloat - outputItem->minFloat) * avgFloat + outputItem->minFloat);
}

// THE PROBLEMATIC FUNCTION THAT FUCKS UP PERFORMANCE
void pushOutputItems(__private TradeupGPU *tradeup,
                    __global float *minFloats,
                    __global float *maxFloats,
                    __global TempAccessID *outcomeCollections,
                    __global TempAccessID *outputIDS)
{
    __private float collectionChances[COLLECTION_END] = {0.0};
    __private int distinctCollectionItems[COLLECTION_END] = {0};

    __private int currentOutputItem = 0;

    for (int i = 0; i < tradeup->totalInputSize; ++i) {
        MarketItem *input = &tradeup->inputs[i];
        collectionChances[input->collection] += (100.0 / tradeup->totalInputSize); 

        for (int oid = 0; oid < input->)
        for (int j = collectionIndexStart; j < collectionIndexEnd; ++j) {
            MarketItem possibleOutput = outputItemsPool[j];
            float itemFloatVal = calculateOutputItemFloat(&possibleOutput, tradeup->avgInputFloat);

            // Ignore incorrect wears
            if (possibleOutput.wear != WEAR_NO_WEAR && possibleOutput.wear != itemFloatValToInt(itemFloatVal)) {
                continue;
            }
            // Ignore duplicates
            bool dup = false;
            for (int i = 0; i < currentOutputItem; ++i) {
                if (tradeup->outputs[i].permID == possibleOutput.permID) {
                    dup = true;
                    break;
                }
            }
            if (dup) continue;

            possibleOutput.floatVal = itemFloatVal;
            pushNormalizedFloat(&possibleOutput, possibleOutput.floatVal);
            tradeup->outputs[currentOutputItem++] = possibleOutput;

            for (int oci = 0; oci < possibleOutput.outcomeCollectionsSize; ++oci) {
                ++distinctCollectionItems[possibleOutput.outcomeCollections[oci]];
            }
        }
    }
    
    // Makes no sense - change later
    for (int i = 0; i < currentOutputItem; ++i) {
        MarketItem *output = &tradeup->outputs[i];
        for (int oci = 0; oci < output->outcomeCollectionsSize; ++oci) {
            int outcomeCollection = output->outcomeCollections[oci];
            output->tradeUpChance = collectionChances[outcomeCollection] / (1 * distinctCollectionItems[outcomeCollection]);
        }
    }

    tradeup->totalOutputSize = currentOutputItem;
}

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

    for (auto &output : outputs) {
        int outcomeCollection = output.outcomeCollections[0];
        output.tradeUpChance = collectionChances[outcomeCollection] / (1 * distinctCollectionItems[outcomeCollection]);
    }

    tradeupCPU.outputs = outputs;
}

float getExpectedPrice(__private TradeupGPU *tradeup)
{
    float expectedPrice = 0.0;

    for (int i = 0; i < tradeup->totalOutputSize; ++i) {
        expectedPrice += (tradeup->outputs[i].tradeUpChance / 100.0) * tradeup->outputs[i].price;
    }
    return expectedPrice;
}

void pushProfitability(__private TradeupGPU *tradeup)
{
    float expectedPrice = getExpectedPrice(tradeup);
    float profitability = (expectedPrice / tradeup->totalInputPrice) * 100;
    float profitabilitySteamTax = ((expectedPrice * 0.85) / tradeup->totalInputPrice) * 100;
    tradeup->profitability = profitability;
    tradeup->profitabilitySteamTax = profitabilitySteamTax;
}

void pushChanceToProfit(__private TradeupGPU *tradeup)
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
