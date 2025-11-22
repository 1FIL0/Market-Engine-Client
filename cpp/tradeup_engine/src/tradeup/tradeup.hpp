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
    float normalizedAvgInputFloat;
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
    float normalizedAvgInputFloat;
    float totalInputPrice;
    float profitability;
    float chanceToProfit;
    float profitabilitySteamTax;
    float chanceToProfitSteamTax;

    TradeupCPU()
    {
        avgInputFloat = 0.0;
        normalizedAvgInputFloat = 0.0;
        totalInputPrice = 0.0;
        profitability = 0.0;
        chanceToProfit = 0.0;
        profitabilitySteamTax = 0.0;
        chanceToProfitSteamTax = 0.0;
    }
};

END_ENGINE_NAMESPACE