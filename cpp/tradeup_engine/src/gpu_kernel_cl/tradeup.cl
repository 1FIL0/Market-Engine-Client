#pragma once

#include "market_item.cl"

// ! MUST BE ALIGNED WITH CPU STRUCT

#define MAX_GPU_TRADEUP_INPUTS 10
#define MAX_GPU_TRADEUP_OUTPUTS 100

#pragma pack(push, 1)
typedef struct Tradeup {
    bool processed;
    MarketItem inputs[MAX_GPU_TRADEUP_INPUTS];
    MarketItem outputs[MAX_GPU_TRADEUP_OUTPUTS];
    int totalOutputSize;
    float avgInputFloat;
    float totalInputPrice;
    float profitability;
    float chanceToProfit;
    float profitabilitySteamTax;
    float chanceToProfitSteamTax;
} Tradeup;
#pragma pack(pop)
