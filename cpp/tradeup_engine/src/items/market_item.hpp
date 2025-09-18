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
* read LICENCE file
*/

#pragma once

#include "namespace.hpp"
#include <cstdint>

START_ENGINE_NAMESPACE_MULTI(ITEM)

//! MUST BE ALIGNED WITH OPENCL STRUCT

#pragma pack(push, 1)
struct MarketItem {
    int tempID;
    uint64_t permID;
    int grade;
    int category;
    int wear;
    float price;
    float priceSteamTax;

    bool tradeupable;
    int collection;
    int outputAmount;
    float floatVal, minFloat, maxFloat;
    float tradeUpChance;

    MarketItem();
    bool operator<(const MarketItem &otherItem) {
        return permID < otherItem.permID;
    }
};
#pragma pack(pop)

END_ENGINE_NAMESPACE