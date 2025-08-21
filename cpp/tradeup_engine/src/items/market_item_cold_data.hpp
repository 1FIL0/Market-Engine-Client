#pragma once

#include "namespace.hpp"
#include <string>

START_ENGINE_NAMESPACE_MULTI(ITEM)

struct MarketItemColdData {
    std::string weaponName;
    std::string skinName;
    
    MarketItemColdData();
};

END_ENGINE_NAMESPACE