#include "market_item.hpp"
#include "namespace.hpp"
#include "tradeup.hpp"
#include <cstddef>
#include <cstdlib>
#include <vector>
#include <omp.h>
#include <cstdint>

START_ENGINE_NAMESPACE_MULTI(CPUOP)

uint64_t getCombinationsAmount(int n, int k);

ITEM::MarketItem getRandomItem(const int grade, const int category, const int forceIndex = -1);
void pushRandomItemBatch(std::vector<ITEM::MarketItem> &batch, const size_t batchSize, const int grade, const int category, const float maxItemPrice);
void pushSingleItemBatch(std::vector<ITEM::MarketItem> &batch, const size_t batchSize, const int grade, const int category, const float maxItemPrice);
void setBatchFloats(std::vector<ITEM::MarketItem> &batch);

// NOT IN USE
//void pushInputFloats(TRADEUP::TradeupCPU &tradeupCPU);
void pushAvgInputFloat(TRADEUP::TradeupCPU &tradeupCPU);
void pushInputsCombinedPrice(TRADEUP::TradeupCPU &tradeupCPU);

void pushOutputItems(TRADEUP::TradeupCPU &tradeupCPU);
float calculateOutputItemFloat(const ITEM::MarketItem &outputItem, const float avgFloat);
std::vector<ITEM::MarketItem> sortOutputTickets(std::vector<ITEM::MarketItem> &outputs);

void pushChanceToProfit(TRADEUP::TradeupCPU &tradeupCPU);
float getExpectedPrice(const std::vector<ITEM::MarketItem> &sortedOutputs);
float getExpectedPriceSteamTax(const std::vector<ITEM::MarketItem> &sortedOutputs);
void pushProfitability(TRADEUP::TradeupCPU &tradeupCPU);

END_ENGINE_NAMESPACE