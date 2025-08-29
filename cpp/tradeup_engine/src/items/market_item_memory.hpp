#pragma once

#include "market_item.hpp"
#include "market_item_cold_data.hpp"
#include "namespace.hpp"
#include <rapidjson/document.h>
#include <vector>
#include "market_item_flat_collections.hpp"

USE_NAMESPACE_SHARE
START_ENGINE_NAMESPACE_MULTI(ITEM)

#define ARR_TRADEUPABLE(DATA) std::array<DATA, 2>
#define ARR_CATEGORY(DATA) std::array<DATA, DEFINITIONS::CATEGORY_END>
#define ARR_COLLECTION(DATA) std::array<DATA, DEFINITIONS::COLLECTION_END>
#define ARR_GRADE(DATA) std::array<DATA, DEFINITIONS::GRADE_END>
#define ARR_WEAR(DATA) std::array<DATA, DEFINITIONS::WEAR_END>

enum {
    TRADEUPABLE_FALSE = 0, TRADEUPABLE_TRUE = 1
};

void loadEverything(void);
rapidjson::Document getReadyItemsDoc(void);
rapidjson::Document getModifiedItemsDoc(void);
void loadMarketItems(void);

void pushMarketItem(const MarketItem &item, const MarketItemColdData &coldData);
void sortMarketItems(void);

const std::vector<MarketItem> &getItems(void);
MarketItemColdData getColdData(const MarketItem &item);
const std::vector<MarketItem> &getItemsCategoryGradeCollection (const int category, const int grade, const int collection);
const std::vector<MarketItem> &getItemsTradeupableCategoryGrade(const bool tradeupable, const int category, const int grade);
const std::vector<MarketItem> &getItemsTradeupableCategoryGradeCollection(const bool tradeupable, const int category, const int grade, const int collection);

// Only used for GPU engine
MarketItemMemoryFlatCollections getItemsTradeupableCategoryGradeCollectionsFlattened(const int category, const int grade);

END_ENGINE_NAMESPACE