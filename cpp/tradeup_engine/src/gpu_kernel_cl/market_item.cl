#pragma once

// ! MUST BE ALIGNED WITH CPU STRUCT

#pragma pack(push, 1)
typedef struct MarketItem 
{
    int tempID;
    ulong permID;
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
} MarketItem;
#pragma pack(pop)
