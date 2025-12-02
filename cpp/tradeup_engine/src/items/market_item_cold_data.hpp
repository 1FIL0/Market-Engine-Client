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
#include "namespace.hpp"
#include <string>
#include <vector>

START_ENGINE_NAMESPACE_MULTI(ITEM)

struct MarketItemColdData {
    std::string weaponName;
    std::string skinName;
    std::vector<TempAccessID> outputTempAccessIDS;
    
    MarketItemColdData();
};

END_ENGINE_NAMESPACE