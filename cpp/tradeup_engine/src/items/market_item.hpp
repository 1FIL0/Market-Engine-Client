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