#* Market Engine Client
#* Copyright (C) 2025 OneFil (1FIL0) https://github.com/1FIL0
#*
#* This program is free software: you can redistribute it and/or modify
#* it under the terms of the GNU General Public License as published by
#* the Free Software Foundation, either version 3 of the License, or
#* (at your option) any later version.
#*
#* This program is distributed in the hope that it will be useful,
#* but WITHOUT ANY WARRANTY; without even the implied warranty of
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#* GNU General Public License for more details.
#*
#* You should have received a copy of the GNU General Public License
#* along with this program.  If not, see <http://www.gnu.org/licenses/>.
#* See LICENCE file.

import sys
from typing import Any, Callable
import path
sys.path.insert(0, path.PATH_SHARE)
import file_handler
import definitions
import logger
from tradeup_def import Tradeup, TradeupInputEntry, TradeupOutputEntry
import tradeup_entry_operations as operations
import hashlib
import item_memory
from time import perf_counter
from item import MarketItem

gTradeups: list[Tradeup] = list()
gTradeupsLoadedCallbacks: list[Callable[[], None]] = list()

def init() -> None:
    loadTradeups()

def loadTradeups() -> None:
    startTime = perf_counter()
    global gTradeups
    clearArrays()
    data = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS))
    for tradeupEntry in data["DATA"]:
        tradeup: Tradeup = Tradeup()
        for inputEntry in tradeupEntry["Inputs"]:
            newInputEntry: TradeupInputEntry = TradeupInputEntry()
            newInputEntry.permID = inputEntry["Perm ID"]
            newInputEntry.weaponName = inputEntry["Weapon"]
            newInputEntry.skinName = inputEntry["Skin"]
            newInputEntry.category = inputEntry["Category"]
            newInputEntry.grade = inputEntry["Grade"]
            newInputEntry.wear = inputEntry["Wear"]
            newInputEntry.floatVal = inputEntry["Float Val"]
            newInputEntry.normalizedFloatVal = inputEntry["Normalized Float Val"]
            tradeup.inputEntries.append(newInputEntry)
        for outputEntry in tradeupEntry["Outputs"]:
            newOutputEntry: TradeupOutputEntry = TradeupOutputEntry()
            newOutputEntry.permID = outputEntry["Perm ID"]
            newOutputEntry.weaponName = outputEntry["Weapon"]
            newOutputEntry.skinName = outputEntry["Skin"]
            newOutputEntry.category = outputEntry["Category"]
            newOutputEntry.grade = outputEntry["Grade"]
            newOutputEntry.wear = outputEntry["Wear"]
            newOutputEntry.floatVal = outputEntry["Float Val"]
            newOutputEntry.normalizedFloatVal = outputEntry["Normalized Float Val"]
            newOutputEntry.moneyGain = outputEntry["Money Gain"]
            newOutputEntry.moneyGainSteamTax = outputEntry["Money Gain Steam Tax"]
            newOutputEntry.tradeupChance = outputEntry["Tradeup Chance"]
            newOutputEntry.outputAmount = outputEntry["Output Amount"]
            tradeup.outputEntries.append(newOutputEntry)
        tradeup.averageInputFloat = tradeupEntry["Average Input Float"]
        tradeup.normalizedAverageInputFloat = tradeupEntry["Normalized Average Input Float"]
        tradeup.chanceToProfit = tradeupEntry["Chance To Profit"]
        tradeup.chanceToProfitSteamTax = tradeupEntry["Chance To Profit Steam Tax"]
        tradeup.dateFound = tradeupEntry["Date Found"]
        tradeup.deviceUsed = tradeupEntry["Device Used"]
        tradeup.profitability = tradeupEntry["Profitability"]
        tradeup.profitabilitySteamTax = tradeupEntry["Profitability Steam Tax"]
        tradeup.totalInputCost = tradeupEntry["Total Input Cost"]
        tradeup.totalOutputs = tradeupEntry["Total Outputs"]
        tradeup.tradeupCategory = definitions.categoryToInt(tradeupEntry["Tradeup Category"])
        tradeup.tradeupGrade = definitions.gradeToInt(tradeupEntry["Tradeup Grade"])
        tradeup.tradeupHash = tradeupEntry["Tradeup Hash"]
        tradeup.favourite = tradeupEntry["Favourite"]
        gTradeups.append(tradeup)
    endTime = perf_counter()
    logger.sendMessage(f"Tradeups loaded in {endTime - startTime:.4f} seconds")
    handleCallbacks()

def clearArrays() -> None:
    global gTradeups
    gTradeups.clear()

def getTradeups() -> list[Tradeup]:
    global gTradeups
    return gTradeups

def recalculateTradeupsFile() -> None:
    startTime = perf_counter()
    logger.sendMessage("Refreshing tradeups")
    data = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS))
    for entry in data["DATA"]:
        inputItemEntries: list[dict[str, Any]] = list()
        outputItemEntries: list[dict[str, Any]] = list()
        for inputItemEntry in entry["Inputs"]:
            inputItem: MarketItem = item_memory.getItemByPermId(inputItemEntry["Perm ID"])
            inputItemEntry["Price"] = inputItem.price
            inputItemEntries.append(inputItemEntry)
        for outputItemEntry in entry["Outputs"]:
            outputItem = item_memory.getItemByPermId(outputItemEntry["Perm ID"])
            outputItemEntry["Price"] = outputItem.price
            outputItemEntries.append(outputItemEntry)
        inputPrice = operations.getItemsCombinedPrice(inputItemEntries)
        entry["Total Input Cost"] = inputPrice
        entry["Chance To Profit"] = operations.getChanceToProfit(inputPrice, outputItemEntries)
        entry["Chance To Profit Steam Tax"] = operations.getChanceToProfitSteamTax(inputPrice, outputItemEntries)
        entry["Profitability"] = operations.getProfitability(inputPrice, outputItemEntries)
        entry["Profitability Steam Tax"] = operations.getProfitabilitySteamTax(inputPrice, outputItemEntries)
        hashTradeup(entry)
    file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS), data)
    endTime = perf_counter()
    logger.sendMessage(f"Tradeups Recalculated in {endTime - startTime:.4f} seconds")

def hashTradeup(entry: dict[str, Any]) -> None:
    hashInput: str = ""
    # ORDER MUST BE IDENTICAL TO C++ VARIANT
    for inputEntry in entry["Inputs"]:
        hashInput += str(inputEntry["Weapon"]) + str(inputEntry["Skin"])
        hashInput += str(inputEntry["Category"])
        hashInput += str(inputEntry["Wear"])
        hashInput += str(inputEntry["Price"])
    for outputEntry in entry["Outputs"]:
        hashInput += str(outputEntry["Weapon"]) + str(outputEntry["Skin"])
        hashInput += str(outputEntry["Category"])
        hashInput += str(outputEntry["Wear"])
        hashInput += str(outputEntry["Price"])
        hashInput += str(outputEntry["Tradeup Chance"])
    hashInput += str(entry["Profitability"])
    hashInput += str(entry["Chance To Profit"])
    digest = hashlib.sha256(hashInput.encode()).hexdigest()
    entry["Tradeup Hash"] = digest

def deleteTradeupFromFile(hash: str) -> None:
    data = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS))
    for tradeupEntry in data["DATA"]:
        if tradeupEntry["Tradeup Hash"] == hash:
            data["DATA"].remove(tradeupEntry)
    file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS), data)

def favouriteTradeupInFile(hash: str, val: bool) -> None:
    data = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS))
    for tradeupEntry in data["DATA"]:
        if tradeupEntry["Tradeup Hash"] == hash:
            tradeupEntry["Favourite"] = val
    file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS), data)

def addTradeupsLoadedCallback(callback: Callable[[], None]) -> None:
    global gTradeupsLoadedCallbacks
    gTradeupsLoadedCallbacks.append(callback)

def handleCallbacks() -> None:
    global gTradeupsLoadedCallbacks
    for callback in gTradeupsLoadedCallbacks:
        callback()