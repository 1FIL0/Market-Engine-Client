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

#include "definitions.cl"
#include "item_id.cl"

// ! MUST BE ALIGNED WITH CPU STRUCT

#define MAX_MARKET_ITEM_COLLECTIONS COLLECTION_END

#pragma pack(push, 1)
typedef struct MarketItem 
{
    TempAccessID tempAccessID;
    PermID permID;
    short grade;
    short category;
    short wear;
    float price;
    float priceSteamTax;

    bool tradeupable;
    short collection;
    float floatVal, normalizedFloatVal, minFloat, maxFloat;
    float tradeUpChance;

    short outcomeCollections[MAX_MARKET_ITEM_COLLECTIONS];
    int outcomeCollectionsSize;
} MarketItem;
#pragma pack(pop)
