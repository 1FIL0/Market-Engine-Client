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

#include "market_item.hpp"
#include "namespace.hpp"
#include "tradeup.hpp"
#include <cstddef>
#include <cstdlib>
#include <vector>
#include <omp.h>
#include <cstdint>

START_ENGINE_NAMESPACE_MULTI(CPUOP)

void makeCombinationTradeup(TRADEUP::TradeupCPU &tradeupCPU, std::vector<ITEM::MarketItem> &combination);
uint64_t getCombinationsAmount(int n, int k);

ITEM::MarketItem getRandomItem(const int grade, const int category, const int forceIndex = -1);
void pushRandomItemBatch(std::vector<ITEM::MarketItem> &batch, const size_t batchSize, const int grade, const int category, const float maxItemPrice);
void pushSingleItemBatch(std::vector<ITEM::MarketItem> &batch, const size_t batchSize, const int grade, const int category, const float maxItemPrice);
void setBatchFloats(std::vector<ITEM::MarketItem> &batch);

// !NOT IN USE
void pushInputFloats(TRADEUP::TradeupCPU &tradeupCPU);
//
void pushAvgInputFloat(TRADEUP::TradeupCPU &tradeupCPU);
void pushAdjustedAvgInputFloat(TRADEUP::TradeupCPU &tradeupCPU);
void pushInputsCombinedPrice(TRADEUP::TradeupCPU &tradeupCPU);

void pushOutputItems(TRADEUP::TradeupCPU &tradeupCPU);
float calculateOutputItemFloat(const ITEM::MarketItem &outputItem, const float avgInputFloat);
float calculateAdjustedOutputItemFloat(const ITEM::MarketItem &outputItem, const float adjustedAvgInputFloat);
std::vector<ITEM::MarketItem> sortOutputTickets(std::vector<ITEM::MarketItem> &outputs);

void pushChanceToProfit(TRADEUP::TradeupCPU &tradeupCPU);
float getExpectedPrice(const std::vector<ITEM::MarketItem> &sortedOutputs);
float getExpectedPriceSteamTax(const std::vector<ITEM::MarketItem> &sortedOutputs);
void pushProfitability(TRADEUP::TradeupCPU &tradeupCPU);

END_ENGINE_NAMESPACE