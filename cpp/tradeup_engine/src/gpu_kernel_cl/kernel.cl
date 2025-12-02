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

#include "market_item.cl"
#include "operations.cl"
#include "tradeup.cl"

#define MAX_COMBINATION_SIZE 10

TradeupGPU processCombination(__global float *minFloats,
                        __global float *maxFloats,
                        __global float *prices,
                        __global TempAccessID *flatOutcomeCollections,
                        __global TempAccessID *outputIDS,
                        __private MarketItem *combination,
                        __private int combinationSize)
{
    __private TradeupGPU tradeup;
    tradeup.totalInputSize = combinationSize;

    for (int i = 0; i < tradeup.totalInputSize; ++i) {
        tradeup.inputs[i] = combination[i];
    }

    pushAvgInputFloat(&tradeup);
    pushNormalizedAvgInputFloat(&tradeup);
    pushTotalInputPrice(&tradeup);
    pushOutputItems(&tradeup, flatCollectionOutputsPool, collectionIndicesStart, collectionIndiciesEnd);
    pushChanceToProfit(&tradeup);
    pushProfitability(&tradeup);

    return tradeup;
}

__kernel void combinationKernel(__global TradeupGPU *tradeups,
                                __global MarketItem *batch,
                                __global float *minFloats,
                                __global float *maxFloats,
                                __global float *prices,

                                __global TempAccessID *flatOutcomeCollections,
                                __global int *flatOutcomeCollectionsIndicesStart,
                                __global int *flatOutcomeCollectionsIndicesEnd,
                                
                                __global TempAccessID *flatOutputIds,
                                __global TempAccessID *flatOutputIdsIndicesStart,
                                __global TempAccessID *flatOutputIdsIndicesEnd,

                                __private short grade,
                                __private uint batchSize,
                                __private ulong combinationsAmount,
                                __private float profitabilityMargin)
{
    ulong gid = get_global_id(0);
    ulong combStart = gid;
    int n = batchSize;

    if (combStart >= combinationsAmount) return;
    int combinationSize = (grade == GRADE_COVERT) ? 5 : 10;

    int localIndices[MAX_COMBINATION_SIZE];
    int combTemp = combStart;
    
    for (int i = 0; i < combinationSize; ++i) {
        localIndices[i] = combTemp % (n - i) + i;
        combTemp /= (n - i);
    }

    MarketItem combination[MAX_COMBINATION_SIZE];
    for (int i = 0; i < combinationSize; ++i) {
        combination[i] = batch[localIndices[i]];
    }

    __private TradeupGPU tradeup = processCombination(minFloats, maxFloats, prices, flatOutcomeCollections, outputIDS, combination, combinationSize);
    if (tradeup.profitability > profitabilityMargin) {
        tradeup.processed = true; // tradeup is replaced by new value and "processed". later set to false when "clearing" tradeups in the host
        tradeups[gid] = tradeup;
    }
}