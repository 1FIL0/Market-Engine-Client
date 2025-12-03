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

// ! MUST BE ALIGNED WITH CPU STRUCT

#define MAX_GPU_TRADEUP_INPUTS 10
#define MAX_GPU_TRADEUP_OUTPUTS 300

#pragma pack(push, 1)
typedef struct TradeupGPU {
    bool processed;
    MarketItem inputs[MAX_GPU_TRADEUP_INPUTS];

    TempAccessID outputIDS[MAX_GPU_TRADEUP_OUTPUTS];
    float outputFloats[MAX_GPU_TRADEUP_OUTPUTS];
    short outputWears[MAX_GPU_TRADEUP_OUTPUTS];
    float outputTradeupChances[MAX_GPU_TRADEUP_OUTPUTS];

    int totalInputSize;
    int totalOutputSize;
    float avgInputFloat;
    float normalizedAvgInputFloat;
    float totalInputPrice;
    float profitability;
    float chanceToProfit;
    float profitabilitySteamTax;
    float chanceToProfitSteamTax;
} TradeupGPU;
#pragma pack(pop)
