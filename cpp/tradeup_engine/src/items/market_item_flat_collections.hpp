#include "definitions.hpp"
#include "market_item.hpp"
#include "namespace.hpp"
#include <vector>
#include <array>

START_ENGINE_NAMESPACE_MULTI(ITEM)
USE_NAMESPACE_SHARE

class MarketItemMemoryFlatCollections {
public:
    std::array<int, DEFINITIONS::COLLECTION_END> collectionsIndicesStart;
    std::array<int, DEFINITIONS::COLLECTION_END> collectionsIndicesEnd;
    std::vector<MarketItem> collectionItemsFlat;

    MarketItemMemoryFlatCollections();
};

END_ENGINE_NAMESPACE