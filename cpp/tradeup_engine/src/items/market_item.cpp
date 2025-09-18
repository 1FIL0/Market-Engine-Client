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
