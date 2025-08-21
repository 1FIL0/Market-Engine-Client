#include "market_item.hpp"
#include "namespace.hpp"
#include <cstring>

USE_NAMESPACE_TRADEUP_ENGINE

ITEM::MarketItem::MarketItem()
{
    tempID = -1;
    permID = 0;
    grade = -1;
    category = -1;
    wear = -1;
    price = -1.0;

    tradeupable = false;
    collection = -1;
    outputAmount = 0;
    floatVal = -1.0;
    minFloat = -1.0;
    maxFloat = -1.0;
    tradeUpChance = -1.0;
}
