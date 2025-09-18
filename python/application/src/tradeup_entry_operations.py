'''
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
'''

import sys
from typing import Any
import path
sys.path.insert(0, path.PATH_SHARE)

def getAvgInputFloat(inputEntries: list[dict[str, Any]]) -> float:
    avgFloat = 0.0
    for inputEntry in inputEntries:
        avgFloat = avgFloat + inputEntry["Float Val"]
    avgFloat = avgFloat / 10.0
    return avgFloat

def getItemsCombinedPrice(itemEntries: list[dict[str, Any]]) -> float:
    totalPrice = 0.0
    for itemEntry in itemEntries:
        totalPrice += itemEntry["Price"]
    return totalPrice

def getChanceToProfit(inputPrice: float, outputEntries:list[dict[str, Any]]) -> float:
    chanceToProfit = 0.0
    for outputEntry in outputEntries:
        if outputEntry["Price"] > inputPrice: chanceToProfit += outputEntry["Tradeup Chance"]
    return chanceToProfit

def getChanceToProfitSteamTax(inputPrice: float, outputEntries: list[dict[str, Any]]) -> float:
    chanceToProfit = 0.0
    for outputEntry in outputEntries:
        if outputEntry["Price Steam Tax"] > inputPrice: chanceToProfit += outputEntry["Tradeup Chance"]
    return chanceToProfit

def getExpectedPrice(outputEntries: list[dict[str, Any]]) -> float:
    expectedPrice = 0.0
    for outputEntry in outputEntries:
        expectedPrice = expectedPrice + (outputEntry["Tradeup Chance"] / 100.0) * outputEntry["Price"]
    return expectedPrice

def getProfitability(totalCost: float, outputEntries: list[dict[str, Any]]) -> float:
    expectedPrice = getExpectedPrice(outputEntries)
    profitability = (expectedPrice / totalCost) * 100
    return profitability

def getProfitabilitySteamTax(totalCost: float, outputEntries: list[dict[str, Any]]) -> float:
    expectedPrice = getExpectedPrice(outputEntries) * 0.85
    profitability = (expectedPrice / totalCost) * 100
    return profitability