       
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
       
       
__constant const int WEAR_FACTORY_NEW = 0;
__constant const int WEAR_MINIMAL_WEAR = 1;
__constant const int WEAR_FIELD_TESTED = 2;
__constant const int WEAR_WELL_WORN = 3;
__constant const int WEAR_BATTLE_SCARRED = 4;
__constant const float FLOAT_MIN_FACTORY_NEW = 0.00;
__constant const float FLOAT_MIN_MINIMAL_WEAR = 0.071;
__constant const float FLOAT_MIN_FIELD_TESTED = 0.151;
__constant const float FLOAT_MIN_WELL_WORN = 0.381;
__constant const float FLOAT_MIN_BATTLE_SCARRED = 0.451;
__constant const float FLOAT_MAX_FACTORY_NEW = 0.07;
__constant const float FLOAT_MAX_MINIMAL_WEAR = 0.15;
__constant const float FLOAT_MAX_FIELD_TESTED = 0.38;
__constant const float FLOAT_MAX_WELL_WORN = 0.45;
__constant const float FLOAT_MAX_BATTLE_SCARRED = 1.0;
__constant const float FLOAT_AVG_FACTORY_NEW = 0.035;
__constant const float FLOAT_AVG_MINIMAL_WEAR = 0.11;
__constant const float FLOAT_AVG_FIELD_TESTED = 0.26;
__constant const float FLOAT_AVG_WELL_WORN = 0.41;
__constant const float FLOAT_AVG_BATTLE_SCARRED = 0.725;
enum {
    COLLECTION_OVERPASS_2024 = 0, COLLECTION_GALLERY, COLLECTION_GRAPHIC_DESIGN, COLLECTION_LIMITED_EDITION_ITEM,
    COLLECTION_SPORT_AND_FIELD, COLLECTION_KILOWATT, COLLECTION_ANUBIS, COLLECTION_REVOLUTION, COLLECTION_RECOIL, COLLECTION_DREAMS_AND_NIGHTMARES,
    COLLECTION_TRAIN_2021, COLLECTION_DUST2_2O21, COLLECTION_MIRAGE_2021, COLLECTION_VERTIGO_2021, COLLECTION_RIPTIDE, COLLECTION_SNAKEBITE,
    COLLECTION_BROKEN_FANG, COLLECTION_CONTROL, COLLECTION_ANCIENT, COLLECTION_HAVOC, COLLECTION_FRACTURE, COLLECTION_PRISMA2,
    COLLECTION_CANALS, COLLECTION_ST_MARC, COLLECTION_NORSE, COLLECTION_SHATTERED_WEB, COLLECTION_CS20, COLLECTION_XRAY,
    COLLECTION_PRISMA, COLLECTION_CLUTCH, COLLECTION_BLACKSITE, COLLECTION_DANGER_ZONE, COLLECTION_NUKE_2018, COLLECTION_INFERNO_2018,
    COLLECTION_HORIZON, COLLECTION_SPECTRUM_2, COLLECTION_HYDRA, COLLECTION_SPECTRUM, COLLECTION_GLOVE, COLLECTION_GAMMA2,
    COLLECTION_GAMMA, COLLECTION_CHROMA3, COLLECTION_WILDFIRE, COLLECTION_REVOLVER_CASE, COLLECTION_SHADOW, COLLECTION_RISING_SUN,
    COLLECTION_GODS_AND_MONSTERS, COLLECTION_CHOP_SHOP, COLLECTION_FALCHION, COLLECTION_CHROMA2, COLLECTION_CHROMA, COLLECTION_VANGUARD,
    COLLECTION_CACHE, COLLECTION_ESPORTS_2014_SUMMER, COLLECTION_BREAKOUT, COLLECTION_BAGGAGE, COLLECTION_OVERPASS, COLLECTION_COBBLESTONE,
    COLLECTION_BANK, COLLECTION_HUNTSMAN, COLLECTION_PHEONIX, COLLECTION_ARMS_DEAL_3, COLLECTION_ESPORTS_2013_WINTER, COLLECTION_WINTER_OFFENSIVE,
    COLLECTION_ITALY, COLLECTION_MIRAGE, COLLECTION_SAFEHOUSE, COLLECTION_DUST2, COLLECTION_LAKE, COLLECTION_TRAIN,
    COLLECTION_ARMS_DEAL_2, COLLECTION_ALPHA, COLLECTION_BRAVO, COLLECTION_ASSAULT, COLLECTION_DUST, COLLECTION_OFFICE,
    COLLECTION_NUKE, COLLECTION_AZTEC, COLLECTION_INFERNO, COLLECTION_ARMS_DEAL, COLLECTION_MILITIA, COLLECTION_VERTIGO,
    COLLECTION_ESPORTS_2013, COLLECTION_TRAIN_2O25, COLLECTION_RADIANT, COLLECTION_BOREAL, COLLECTION_ASCENT, COLLECTION_FEVER,
    COLLECTION_END
};
float wearToMinFloat(__private int wear)
{
    switch (wear) {
        case WEAR_FACTORY_NEW: {return FLOAT_MIN_FACTORY_NEW;}; break;
        case WEAR_MINIMAL_WEAR: {return FLOAT_MIN_MINIMAL_WEAR;}; break;
        case WEAR_FIELD_TESTED: {return FLOAT_MIN_FIELD_TESTED;}; break;
        case WEAR_WELL_WORN: {return FLOAT_MIN_WELL_WORN;}; break;
        case WEAR_BATTLE_SCARRED: {return FLOAT_MIN_BATTLE_SCARRED;}; break;
    }
    return -1.0;
}
float wearToMaxFloat(__private int wear)
{
    switch (wear) {
        case WEAR_FACTORY_NEW: {return FLOAT_MAX_FACTORY_NEW;} break;
        case WEAR_MINIMAL_WEAR: {return FLOAT_MAX_MINIMAL_WEAR;} break;
        case WEAR_FIELD_TESTED: {return FLOAT_MAX_FIELD_TESTED;} break;
        case WEAR_WELL_WORN: {return FLOAT_MAX_WELL_WORN;} break;
        case WEAR_BATTLE_SCARRED: {return FLOAT_MAX_BATTLE_SCARRED;} break;
    }
    return -1.0;
}
float itemFloatValToInt(__private float val)
{
    if (val >= 0.0 && val <= FLOAT_MAX_FACTORY_NEW) {return WEAR_FACTORY_NEW;}
    if (val >= 0.0 && val <= FLOAT_MAX_MINIMAL_WEAR) {return WEAR_MINIMAL_WEAR;}
    if (val >= 0.0 && val <= FLOAT_MAX_FIELD_TESTED) {return WEAR_FIELD_TESTED;}
    if (val >= 0.0 && val <= FLOAT_MAX_WELL_WORN) {return WEAR_WELL_WORN;}
    if (val >= 0.0 && val <= FLOAT_MAX_BATTLE_SCARRED) {return WEAR_BATTLE_SCARRED;}
    return -1.0;
}
       
#pragma pack(push, 1)
typedef struct Tradeup {
    bool processed;
    MarketItem inputs[10];
    MarketItem outputs[100];
    int totalOutputSize;
    float avgInputFloat;
    float totalInputPrice;
    float profitability;
    float chanceToProfit;
    float profitabilitySteamTax;
    float chanceToProfitSteamTax;
} Tradeup;
#pragma pack(pop)
void pushTotalInputPrice(__private Tradeup *tradeup)
{
    float totalPrice = 0.0;
    for (int i = 0; i < 10; ++i) {
        totalPrice += tradeup->inputs[i].price;
        tradeup->totalInputPrice = totalPrice;
    }
}
void pushAvgInputFloat(__private Tradeup *tradeup)
{
    float avgFloat = 0.0;
    for (int i = 0; i < 10; ++i) {
        avgFloat += tradeup->inputs[i].floatVal;
    }
    avgFloat /= 10.0;
    tradeup->avgInputFloat = avgFloat;
}
float calculateOutputItemFloat(__private const MarketItem *outputItem,
                                __private float avgFloat)
{
    return ((outputItem->maxFloat - outputItem->minFloat) * avgFloat + outputItem->minFloat);
}
void sortOutputItemsTickets(__private MarketItem *outputTickets,
                            __private int outputTicketsSize,
                            __private MarketItem *sortedOutputs,
                            __private int *sortedOutputsSize)
{
    __private MarketItem singleItems[256];
    __private int currentSingleItems = 0;
    __private int collectionAmounts[COLLECTION_END];
    for (int i = 0; i < outputTicketsSize; ++i) {
        bool dup = false;
        for (int j = 0; j < currentSingleItems; ++j) {
            if (singleItems[j].tempID == outputTickets[i].tempID) {
                ++singleItems[j].outputAmount;
                ++collectionAmounts[singleItems[j].collection];
                dup = true;
                break;
            }
        }
        if (dup) {
            continue;
        }
        singleItems[currentSingleItems] = outputTickets[i];
        singleItems[currentSingleItems].outputAmount = 1;
        ++collectionAmounts[outputTickets[i].collection];
        ++currentSingleItems;
    }
    for (int i = 0; i < currentSingleItems; ++i) {
        int totalCollectionOutputs = collectionAmounts[singleItems[i].collection];
        singleItems[i].tradeUpChance = (((float)totalCollectionOutputs / outputTicketsSize) * singleItems[i].outputAmount / totalCollectionOutputs) * 100;
    }
    for (int i = 0; i < currentSingleItems; ++i) {
        sortedOutputs[i] = singleItems[i];
    }
    *sortedOutputsSize = currentSingleItems;
}
void pushOutputs(__private Tradeup *tradeup,
                __global MarketItem *outputItemsPool,
                __global int *collectionIndicesStart,
                __global int *collectionIndiciesEnd)
{
    __private int currentTicket = 0;
    __private MarketItem outputTickets[100];
    for (int i = 0; i < 10; ++i) {
        int collectionIndexStart = collectionIndicesStart[tradeup->inputs[i].collection];
        int collectionIndexEnd = collectionIndiciesEnd[tradeup->inputs[i].collection];
        for (int j = collectionIndexStart; j < collectionIndexEnd; ++j) {
            MarketItem itemTicket = outputItemsPool[j];
            float itemFloatVal = calculateOutputItemFloat(&itemTicket, tradeup->avgInputFloat);
            if (itemTicket.wear != itemFloatValToInt(itemFloatVal)) {
                continue;
            }
            itemTicket.floatVal = itemFloatVal;
            outputTickets[currentTicket++] = itemTicket;
        }
    }
    __private int outputSize = currentTicket;
    __private int sortedOutputsSize;
    sortOutputItemsTickets(outputTickets, outputSize, tradeup->outputs, &sortedOutputsSize);
    tradeup->totalOutputSize = sortedOutputsSize;
}
float getExpectedPrice(__private Tradeup *tradeup)
{
    float expectedPrice = 0.0;
    for (int i = 0; i < tradeup->totalOutputSize; ++i) {
        expectedPrice += (tradeup->outputs[i].tradeUpChance / 100.0) * tradeup->outputs[i].price;
    }
    return expectedPrice;
}
void pushProfitability(__private Tradeup *tradeup)
{
    float expectedPrice = getExpectedPrice(tradeup);
    float profitability = (expectedPrice / tradeup->totalInputPrice) * 100;
    float profitabilitySteamTax = ((expectedPrice * 0.85) / tradeup->totalInputPrice) * 100;
    tradeup->profitability = profitability;
    tradeup->profitabilitySteamTax = profitabilitySteamTax;
}
void pushChanceToProfit(__private Tradeup *tradeup)
{
    float chanceToProfit = 0.0;
    float chanceToProfitSteamTax = 0.0;
    for (int i = 0; i < tradeup->totalOutputSize; ++i) {
        if (tradeup->outputs[i].price > tradeup->totalInputPrice) {
            chanceToProfit += tradeup->outputs[i].tradeUpChance;
        }
        if (tradeup->outputs[i].priceSteamTax > tradeup->totalInputPrice) {
            chanceToProfitSteamTax += tradeup->outputs[i].tradeUpChance;
        }
    }
    tradeup->chanceToProfit = chanceToProfit;
    tradeup->chanceToProfitSteamTax = chanceToProfitSteamTax;
}
Tradeup processCombination(__global MarketItem *flatCollectionOutputsPool,
                        __global int *collectionIndicesStart,
                        __global int *collectionIndiciesEnd,
                        __private MarketItem *combination)
{
    __private Tradeup tradeup;
    for (int i = 0; i < 10; ++i) {
        tradeup.inputs[i] = combination[i];
    }
    pushAvgInputFloat(&tradeup);
    pushTotalInputPrice(&tradeup);
    pushOutputs(&tradeup, flatCollectionOutputsPool, collectionIndicesStart, collectionIndiciesEnd);
    pushChanceToProfit(&tradeup);
    pushProfitability(&tradeup);
    return tradeup;
}
__kernel void combinationKernel(__global Tradeup *tradeups,
                                __global MarketItem *batch,
                                __global MarketItem *flatCollectionOutputsPool,
                                __global int *collectionIndicesStart,
                                __global int *collectionIndicesEnd,
                                __private long batchSize,
                                __private ulong combinationsAmount,
                                __private float profitabilityMargin)
{
    ulong gid = get_global_id(0);
    ulong combStart = gid;
    int n = batchSize;
    if (combStart >= combinationsAmount) return;
    int localIndices[10];
    int combTemp = combStart;
    for (int i = 0; i < 10; ++i) {
        localIndices[i] = combTemp % (n - i) + i;
        combTemp /= (n - i);
    }
    MarketItem combination[10];
    for (int i = 0; i < 10; ++i) {
        combination[i] = batch[localIndices[i]];
    }
    __private Tradeup tradeup = processCombination(flatCollectionOutputsPool, collectionIndicesStart, collectionIndicesEnd, combination);
    if (tradeup.profitability > profitabilityMargin) {
        tradeups[gid] = tradeup;
        tradeup.processed = true;
    }
}
