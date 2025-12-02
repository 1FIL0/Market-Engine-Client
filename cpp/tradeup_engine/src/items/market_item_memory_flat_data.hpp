#pragma once

#include "market_item.hpp"
#include "namespace.hpp"
#include <vector>

START_ENGINE_NAMESPACE_MULTI(ITEM)

struct MarketItemMemoryFlatData {
    std::vector<int> outcomeCollections;
    std::vector<int> outcomeCollectionsStartIndices;
    std::vector<int> outcomeCollectionsEndIndices;
    
    std::vector<TempAccessID> outputItemIds;
    std::vector<int> outputItemIdsStartIndices;
    std::vector<int> outputItemIdsEndIndices;
    
    std::vector<float> minFloats;
    std::vector<float> maxFloats;
};

END_ENGINE_NAMESPACE