#include "market_item.cl"
#include "operations.cl"
#include "tradeup.cl"

Tradeup processCombination(__global MarketItem *flatCollectionOutputsPool,
                        __global int *collectionIndicesStart,
                        __global int *collectionIndiciesEnd,
                        __private MarketItem *combination)
{
    __private Tradeup tradeup;
    
    for (int i = 0; i < MAX_GPU_TRADEUP_INPUTS; ++i) {
        tradeup.inputs[i] = combination[i];
    }

    pushAvgInputFloat(&tradeup);
    pushTotalInputPrice(&tradeup);
    pushOutputs(&tradeup, flatCollectionOutputsPool, collectionIndicesStart, collectionIndiciesEnd);
    pushChanceToProfit(&tradeup);
    pushProfitability(&tradeup);

    return tradeup;
}

__kernel void combinationKernel(__global Tradeup *tradeups,
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

    __private Tradeup tradeup = processCombination(flatCollectionOutputsPool, collectionIndicesStart, collectionIndicesEnd, combination);
    if (tradeup.profitability > profitabilityMargin) {
        tradeup.processed = true; // tradeup is replaced by new value and "processed". later set to false when "clearing" tradeups in the host
        tradeups[gid] = tradeup;
    }
}