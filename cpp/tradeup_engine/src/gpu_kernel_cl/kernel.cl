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

TradeupGPU processCombination(__global MarketItem *flatCollectionOutputsPool,
                        __global int *collectionIndicesStart,
                        __global int *collectionIndiciesEnd,
                        __private MarketItem *combination)
{
    __private TradeupGPU tradeup;
    
    for (int i = 0; i < MAX_GPU_TRADEUP_INPUTS; ++i) {
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
                                __global MarketItem *flatCollectionOutputsPool,
                                __global int *collectionIndicesStart,
                                __global int *collectionIndicesEnd,
                                __private uint batchSize,
                                __private ulong combinationsAmount,
                                __private float profitabilityMargin)
{
    ulong gid = get_global_id(0);
    ulong combStart = gid;
    int n = batchSize;

    if (combStart >= combinationsAmount) return;

    int localIndices[10];
    int combTemp = combStart;
    
    for (int i = 0; i < 10; ++i) {
        localIndices[i] = combTemp % (n - i) + i;
        combTemp /= (n - i);
    }

    MarketItem combination[10];
    for (int i = 0; i < 10; ++i) {
        combination[i] = batch[localIndices[i]];
    }

    __private TradeupGPU tradeup = processCombination(flatCollectionOutputsPool, collectionIndicesStart, collectionIndicesEnd, combination);
    if (tradeup.profitability > profitabilityMargin) {
        tradeup.processed = true; // tradeup is replaced by new value and "processed". later set to false when "clearing" tradeups in the host
        tradeups[gid] = tradeup;
    }
}