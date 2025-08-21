#pragma once

#include "market_item.hpp"
#include "namespace.hpp"
#include "tradeup.hpp"
#include <cstdint>
#include <vector>

START_ENGINE_NAMESPACE_MULTI(COMPCPU)

void init(void);
void getDeviceData(void);
void startCompute(void);
void logComputeDiagnostics(const int category, const int grade, const std::vector<ITEM::MarketItem> batch, const uint64_t currentBatch, const uint64_t combinationsAmount);
void processCombinations(const std::vector<ITEM::MarketItem> &batch, const uint64_t combinationsAmount);
void yieldCombination(const std::vector<ITEM::MarketItem> &combination);
void saveTradeupToFile(TRADEUP::TradeupCPU &tradeupCPU);

END_ENGINE_NAMESPACE