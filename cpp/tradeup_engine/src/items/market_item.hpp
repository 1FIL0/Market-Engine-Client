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

#include "namespace.hpp"
#include <cstdint>
#include "definitions.hpp"

START_ENGINE_NAMESPACE_MULTI(ITEM)
USE_NAMESPACE_SHARE

//! MUST BE ALIGNED WITH OPENCL STRUCT
#define MAX_MARKET_ITEM_COLLECTIONS DEFINITIONS::COLLECTION_END

#pragma pack(push, 1)
struct MarketItem {
    uint64_t permID;          
    float price;           
    float priceSteamTax;   
    float floatVal;        
    float normalizedFloatVal;
    float minFloat;       
    float maxFloat;       
    float tradeUpChance;  
    int tempAccessID;     
    int outcomeCollectionsSize;
    short grade;          
    short category;       
    short wear;           
    short collection;     
    bool tradeupable;     
    short outcomeCollections[MAX_MARKET_ITEM_COLLECTIONS]; 

    MarketItem();

    bool operator<(const MarketItem &otherItem) {
        return permID < otherItem.permID;
    }

    bool operator==(const MarketItem &otherItem) {
        return permID == otherItem.permID && tempAccessID == otherItem.tempAccessID && wear == otherItem.wear;
    }
};
#pragma pack(pop)

END_ENGINE_NAMESPACE