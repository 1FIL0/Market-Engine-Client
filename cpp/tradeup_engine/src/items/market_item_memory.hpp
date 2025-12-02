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
void createFlattenedData(void);
void sendCorruptedItemError(const MarketItem &item);

const MarketItem &getItem(const TempAccessID ID);
const std::vector<MarketItem> &getItems(void);
MarketItemColdData getColdData(const MarketItem &item);
const std::vector<MarketItem> &getItemsCategoryGradeCollection (const int category, const int grade, const int collection);
const std::vector<MarketItem> &getItemsTradeupableCategoryGrade(const bool tradeupable, const int category, const int grade);
const std::vector<MarketItem> &getItemsTradeupableCategoryGradeCollection(const bool tradeupable, const int category, const int grade, const int collection);
const std::vector<TempAccessID> &getOutputsTempIDS(const TempAccessID ID);
const std::vector<float> &getMinFloats(void);
const std::vector<float> &getMaxFloats(void);

// Only used for GPU engine
MarketItemMemoryFlatCollections getItemsTradeupableCategoryGradeCollectionsFlattened(const int category, const int grade);

END_ENGINE_NAMESPACE