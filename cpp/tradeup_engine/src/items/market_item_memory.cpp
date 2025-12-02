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
#include "namespace.hpp"
#include <array>
#include <cstdlib>
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

std::vector<std::vector<TempAccessID>> g_outputItemIDS;
std::vector<float> g_minFloats;
std::vector<float> g_maxFloats;

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
                marketItem.outcomeCollections[marketItem.outcomeCollectionsSize++] = outcomeCollection;
            }
        }
        else {
            marketItem.outcomeCollections[marketItem.outcomeCollectionsSize++] = marketItem.collection;
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
            marketItem.outputTempAccessIDS[marketItem.outputTempAccessIDSSize++] = outputTempAccessID;
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
        
        for (int oci = 0; oci < item.outcomeCollectionsSize; ++oci) {
            int outcomeCollection = item.outcomeCollections[oci];
            g_itemsTradeCategoryGradeCollection[item.tradeupable][item.category][item.grade][outcomeCollection].push_back(item);
            g_itemsCategoryGradeCollection[item.category][item.grade][outcomeCollection].push_back(item);
        }
    }

    LOGGER::sendMessage("Items loaded: " + std::to_string(g_marketItems.size()));
}

void ITEM::createFlattenedData(void)
{
    size_t marketItemsSize = g_marketItems.size();
    g_outputItemIDS.resize(marketItemsSize);
    g_minFloats.resize(marketItemsSize);
    g_maxFloats.resize(marketItemsSize);
    
    for (auto &item : g_marketItems) {
        for (int i = 0; i < item.outputTempAccessIDSSize; ++i) {
            TempAccessID outputTempAccessID = item.outputTempAccessIDS[i];
            g_outputItemIDS[item.tempAccessID].push_back(outputTempAccessID);
        }
        g_minFloats[item.tempAccessID] = item.minFloat;
        g_maxFloats[item.tempAccessID] = item.maxFloat;
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

const std::vector<float> &getMinFloats(void)
{
    return g_minFloats;
}

const std::vector<float> &getMaxFloats(void)
{
    return g_maxFloats;
}

ITEM::MarketItemMemoryFlatCollections ITEM::getItemsTradeupableCategoryGradeCollectionsFlattened(const int category, const int grade)
{
    int itemCounter = 0;
    MarketItemMemoryFlatCollections flatCols;
    ARR_COLLECTION(std::vector<MarketItem>) &colVectorsArr = g_itemsCategoryGradeCollection[category][grade];

    for (int collection = 0; collection < DEFINITIONS::COLLECTION_END; ++collection) {
        flatCols.collectionsIndicesStart[collection] = itemCounter;
        auto &colVec = colVectorsArr[collection];
        for (auto &item : colVec) {
            flatCols.collectionItemsFlat.push_back(item);
            ++itemCounter;
        }
        flatCols.collectionsIndicesEnd[collection] = itemCounter;
    }

    return flatCols;

}
