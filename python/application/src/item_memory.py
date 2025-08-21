import sys
import os
from typing import Callable
import path
sys.path.insert(0, path.PATH_SHARE)
import file_handler
import definitions
from item import MarketItem
import logger
from time import perf_counter

gItemsAll: list[MarketItem] = []
gItemsCollectionCategoryGradeWear: list[list[list[list[list[MarketItem]]]]] = list() # X_X
gItemsAllByPermIDLookup: dict[int, MarketItem] = {}
gItemsLoadedCallbacks: list[Callable[[], None]] = list()

def init():
    loadItems()

def loadItems():
    startTime = perf_counter()

    global gItemsAll
    global gItemsCollectionCategoryGradeWear
    global gItemsAllByPermIDLookup

    if not os.path.exists(definitions.PATH_DATA_CLIENT_READY_ITEMS) or not os.path.exists(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS): return
    readyItemsData = file_handler.loadJson(definitions.PATH_DATA_CLIENT_READY_ITEMS)
    modifiedItemsData = file_handler.loadJson(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS)
    resetArrays()

    modifiedLookup = {item["Perm ID"]: item for item in modifiedItemsData["DATA"]}
    for data in readyItemsData["DATA"]:
        grade: int = definitions.gradeToInt(data["Grade"])
        category: int = definitions.categoryToInt(data["Category"])
        wear = definitions.wearToInt(data["Wear"])
        collection = definitions.collectionToInt(data["Collection"])

        if grade == -1 or category == -1:
            logger.errorMessage(f"Corrupted item {data["Weapon Name"]} {data["Skin Name"]}")
            continue

        readyItem: MarketItem = MarketItem()
        readyItem.tempID = data["Temp ID"]
        readyItem.permID = data["Perm ID"]
        readyItem.weaponName = data["Weapon Name"]
        readyItem.skinName = data["Skin Name"]
        readyItem.fullName = data["Full Name"]
        readyItem.grade = grade
        readyItem.category = category
        # skip these items cuz they have null prices and shit. useless anyway
        if readyItem.category == definitions.consts.CATEGORY_SOUVENIR:
            continue
        readyItem.wear = wear
        readyItem.marketPrice = data["Market Price"]
        readyItem.price = readyItem.marketPrice
        readyItem.collection = collection
        readyItem.minFloat = data["Min Float"]
        readyItem.maxFloat = data["Max Float"]
        readyItem.tradeupable = data["Tradeupable"]
        readyItem.imageUrl = data["Image URL"]
        readyItem.imageName = data["Image Name"]
        readyItem.steamMarketUrl = data["Steam Market URL"]

        modifiedEntry = modifiedLookup.get(readyItem.permID)
        if modifiedEntry:
            readyItem.useModifiedState = modifiedEntry["Use Modified State"]
            readyItem.modifiedPrice = modifiedEntry["Modified Price"]
            if readyItem.useModifiedState:
                readyItem.price = readyItem.modifiedPrice
        readyItem.priceSteamTax = readyItem.price * 0.85

        # Assign to collection
        if collection != -1:
            gItemsCollectionCategoryGradeWear[collection][category][grade][wear].append(readyItem)

        gItemsAll.append(readyItem)
    gItemsAllByPermIDLookup = {item.permID: item for item in gItemsAll}
    endTime = perf_counter()
    logger.sendMessage(f"Ready items loaded in {endTime - startTime:.4f} seconds")
    handleCallbacks()

def handleCallbacks():
    global gItemsLoadedCallbacks
    for callback in gItemsLoadedCallbacks:
        callback()

def resetArrays():
    global gItemsAll
    global gItemsCollectionCategoryGradeWear
    gItemsCollectionCategoryGradeWear = [
        [
            [
                [
                    [

                    ] 
                    for _ in range(definitions.consts.WEAR_MAX)
                ]
                for _ in range(definitions.consts.GRADE_MAX)
            ]
            for _ in range(definitions.consts.CATEGORY_MAX)
        ]
        for _ in range(definitions.consts.COLLECTION_MAX)
    ]
    gItemsAll.clear()

def getAllItems():
    global gItemsAll
    return gItemsAll

def getItemsCollectionCategoryGradeWear(collection: int, category: int, grade: int, wear: int):
    global gItemsCollectionCategoryGradeWear
    return gItemsCollectionCategoryGradeWear[collection][category][grade][wear]

def getItemsByName(items: list[MarketItem], name: str):
    sortedItems: list[MarketItem] = list()
    for item in items:
        if name.lower() in item.fullName.lower():
            sortedItems.append(item)
    return sortedItems

def getItemByPermId(permID: int) -> MarketItem:
    return gItemsAllByPermIDLookup.get(permID, MarketItem())

def addReadyItemsLoadedCallback(callback: Callable[[], None]) -> None:
    global gItemsLoadedCallbacks
    gItemsLoadedCallbacks.append(callback)