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

#include "market_item_memory.hpp"
#include "definitions.hpp"
#include "file_handler.hpp"
#include "logger.hpp"
#include "market_item.hpp"
#include "market_item_cold_data.hpp"
#include "market_item_memory_flat_data.hpp"
#include "namespace.hpp"
#include <array>
#include <cstdlib>
#include <iostream>
#include <rapidjson/document.h>
#include <string>
#include <unordered_map>
#include <vector>

USE_NAMESPACE_SHARE
USE_NAMESPACE_TRADEUP_ENGINE
USE_NAMESPACE_TRADEUP_ENGINE_MULTI(ITEM)

std::vector<MarketItem> g_marketItems;
std::unordered_map<TempAccessID, MarketItemColdData> g_itemsColdData;
ARR_TRADEUPABLE(ARR_CATEGORY(ARR_GRADE(std::vector<MarketItem>)))                   g_itemsTradeCategoryGrade;
ARR_TRADEUPABLE(ARR_CATEGORY(ARR_GRADE(ARR_COLLECTION(std::vector<MarketItem>))))   g_itemsTradeCategoryGradeCollection;
ARR_CATEGORY(ARR_GRADE(ARR_COLLECTION(std::vector<MarketItem>)))                    g_itemsCategoryGradeCollection;
MarketItemMemoryFlatData g_flatData;

void ITEM::loadEverything(void)
{
    loadMarketItems();
    sortMarketItems();
    createFlattenedData();
}

void ITEM::loadMarketItems(void)
{
    LOGGER::sendMessage("Loading Items");
    
    rapidjson::Document readyDoc, modifiedDoc;
    FILES::parseDocSanitizeDataArray(PATH_DATA_CLIENT_READY_ITEMS, readyDoc);
    FILES::parseDocSanitizeDataArray(PATH_DATA_CLIENT_MODIFIED_ITEMS, modifiedDoc);
    rapidjson::Value &readyDataDoc = readyDoc["DATA"];
    rapidjson::Value &modifiedDataDoc = modifiedDoc["DATA"];
    
    if (readyDataDoc.Size() == 0) {
        LOGGER::sendMessage("ERROR, No items found, scan with sonar first");
        exit(-1);
    }

    for (rapidjson::SizeType ri = 0; ri < readyDataDoc.Size(); ++ri) {
        const auto &readyJsonItem = readyDataDoc[ri];
        MarketItem marketItem;
        MarketItemColdData coldData;
        coldData.weaponName = readyJsonItem["Weapon Name"].GetString();
        coldData.skinName = readyJsonItem["Skin Name"].GetString();
        marketItem.tempAccessID = readyJsonItem["Temp Access ID"].GetInt();
        marketItem.permID = readyJsonItem["Perm ID"].GetUint64();
        marketItem.category = DEFINITIONS::categoryToInt(readyJsonItem["Category"].GetString());
        marketItem.grade = DEFINITIONS::gradeToInt(readyJsonItem["Grade"].GetString());
        marketItem.wear = DEFINITIONS::wearToInt(readyJsonItem["Wear"].GetString());
        marketItem.minFloat = readyJsonItem["Min Float"].GetFloat();
        marketItem.maxFloat = readyJsonItem["Max Float"].GetFloat();

        // get modified items and set price accordingly
        marketItem.price = readyJsonItem["Market Price"].GetFloat();
        for (rapidjson::SizeType mi = 0; mi < modifiedDataDoc.Size(); ++mi) {
            const auto &modifiedJsonItem = modifiedDataDoc[mi];
            if (modifiedJsonItem["Perm ID"].GetUint64() != marketItem.permID) continue;
            marketItem.price = (modifiedJsonItem["Use Modified State"].GetBool()) ? modifiedJsonItem["Modified Price"].GetFloat() : readyJsonItem["Market Price"].GetFloat();
            break;
        }
        if (marketItem.price == -1 || marketItem.price == 0) {
            LOGGER::sendMessage("Item " + coldData.weaponName + " " + coldData.skinName + " " + DEFINITIONS::categoryToString(marketItem.category) + " " + DEFINITIONS::wearToString(marketItem.wear) + " Has a corrupted price!");
        }
        marketItem.priceSteamTax = marketItem.price * 0.87;

        marketItem.tradeupable = readyJsonItem["Tradeupable"].GetBool();
        marketItem.collection = DEFINITIONS::collectionToInt(readyJsonItem["Collection"].GetString());

        // Star / Contraband items aren't in any collections but the outcomes still depend on their crates
        if (marketItem.grade == DEFINITIONS::GRADE_STAR || marketItem.grade == DEFINITIONS::GRADE_CONTRABAND) {
            for (auto &outcomeCollectionEntry : readyJsonItem["Crates"].GetArray()) {
                int crate = DEFINITIONS::crateToInt(outcomeCollectionEntry.GetString());
                int outcomeCollection = DEFINITIONS::crateToCollection(crate);
                coldData.outcomeCollections.push_back(outcomeCollection);
            }
        }
        else {
            coldData.outcomeCollections.push_back(marketItem.collection);
        }

        // Star / Contraband items aren't in any collections. rather in crates.
        if ((marketItem.collection == -1) && (marketItem.grade != DEFINITIONS::GRADE_STAR && marketItem.grade != DEFINITIONS::GRADE_CONTRABAND)) {
            LOGGER::sendMessage("Item not in collection " + coldData.weaponName + " " + coldData.skinName);
            continue;
        }
        if (marketItem.grade == -1) {
            LOGGER::sendMessage("Item has no suitable grades " + coldData.weaponName + " " + coldData.skinName);
            continue;
        }

        // Outputs
        for (auto &outputEntry : readyJsonItem["Possible Outputs"].GetArray()) {
            TempAccessID outputTempAccessID = outputEntry["Output Temp Access ID"].GetInt();
            coldData.outputTempAccessIDS.push_back(outputTempAccessID);
        }

        pushMarketItem(marketItem, coldData);
    }
}

void ITEM::pushMarketItem(const ITEM::MarketItem &item, const ITEM::MarketItemColdData &coldData)
{
    g_marketItems.push_back(item);
    g_itemsColdData.insert(std::make_pair(item.permID, coldData));
}

void ITEM::sortMarketItems(void)
{
    for (const auto &item : g_marketItems) {
        auto coldData = getColdData(item);

        if (item.grade == -1) {
            sendCorruptedItemError(item);
            continue;
        }
        else {
            g_itemsTradeCategoryGrade[item.tradeupable][item.category][item.grade].push_back(item);
        }
        
        for (auto &outcomeCollection : coldData.outcomeCollections) {
            g_itemsTradeCategoryGradeCollection[item.tradeupable][item.category][item.grade][outcomeCollection].push_back(item);
            g_itemsCategoryGradeCollection[item.category][item.grade][outcomeCollection].push_back(item);
        }
    }

    LOGGER::sendMessage("Items loaded: " + std::to_string(g_marketItems.size()));
}

void ITEM::createFlattenedData(void)
{   
    for (auto &item : g_marketItems) {
        ITEM::MarketItemColdData coldData = getColdData(item);

        static int outputItemIdIndex = 0;
        g_flatData.outputItemIdsStartIndices.push_back(outputItemIdIndex);
        for (auto &outputTempID : coldData.outputTempAccessIDS) {
            g_flatData.outputItemIds.push_back(outputTempID);
            ++outputItemIdIndex;
        }
        g_flatData.outputItemIdsEndIndices.push_back(outputItemIdIndex);

        static int outcomeCollectionIndex = 0;
        g_flatData.outcomeCollectionsStartIndices.push_back(outcomeCollectionIndex);
        for (auto &outcomeCollection : coldData.outcomeCollections) {
            g_flatData.outcomeCollections.push_back(outcomeCollection);
            ++outcomeCollectionIndex;
        }
        g_flatData.outcomeCollectionsEndIndices.push_back(outcomeCollectionIndex);

        g_flatData.minFloats.push_back(item.minFloat);
        g_flatData.maxFloats.push_back(item.maxFloat);
    }
}

void ITEM::sendCorruptedItemError(const ITEM::MarketItem &item)
{
    auto data = getColdData(item);
    LOGGER::sendMessage("ERROR, CORRUPTED ITEM: " + data.weaponName + " " + data.skinName);
}

const ITEM::MarketItem &ITEM::getItem(const ITEM::TempAccessID ID)
{
    return g_marketItems[ID];
}

const std::vector<ITEM::MarketItem> &ITEM::getItems(void)
{
    return g_marketItems;
}

ITEM::MarketItemColdData ITEM::getColdData(const ITEM::MarketItem &item)
{
    if (g_itemsColdData.find(item.permID) == g_itemsColdData.end()) {
        LOGGER::sendMessage("Item cold data doesn't exist. Perm ID: " + std::to_string(item.permID));
        return ITEM::MarketItemColdData();
    }
    return g_itemsColdData.at(item.permID);
}

const std::vector<ITEM::MarketItem> &ITEM::getItemsCategoryGradeCollection(const int category, const int grade, const int collection)
{
    return g_itemsCategoryGradeCollection[category][grade][collection];
}

const std::vector<ITEM::MarketItem> &ITEM::getItemsTradeupableCategoryGrade(const bool tradeupable, const int category, const int grade)
{
    return g_itemsTradeCategoryGrade[tradeupable][category][grade];
}

const std::vector<ITEM::MarketItem> &ITEM::getItemsTradeupableCategoryGradeCollection(const bool tradeupable, const int category, const int grade, const int collection)
{
    return g_itemsTradeCategoryGradeCollection[tradeupable][category][grade][collection];
}

const ITEM::MarketItemMemoryFlatData &ITEM::getFlatData(void)
{
    return g_flatData;
}