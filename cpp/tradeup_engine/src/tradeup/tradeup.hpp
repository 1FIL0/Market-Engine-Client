#pragma once

#include "market_item.hpp"
#include "namespace.hpp"
#include <vector>

START_ENGINE_NAMESPACE_MULTI(TRADEUP)

// ! MUST BE ALIGNED WITH OPENCL STRUCT

#define MAX_GPU_TRADEUP_INPUTS 10
#define MAX_GPU_TRADEUP_OUTPUTS 100

#pragma pack(push, 1)
struct TradeupGPU {
    bool processed;
    ITEM::MarketItem inputs[MAX_GPU_TRADEUP_INPUTS];
    ITEM::MarketItem outputs[MAX_GPU_TRADEUP_OUTPUTS];
    int totalOutputSize;
    float avgInputFloat;
    float totalInputPrice;
    float profitability;
    float chanceToProfit;
    float profitabilitySteamTax;
    float chanceToProfitSteamTax;
};
#pragma pack(pop)

struct TradeupCPU {
    std::vector<ITEM::MarketItem> inputs;
    std::vector<ITEM::MarketItem> outputs;
    float avgInputFloat;
    float totalInputPrice;
    float profitability;
    float chanceToProfit;
    float profitabilitySteamTax;
    float chanceToProfitSteamTax;
};

END_ENGINE_NAMESPACE