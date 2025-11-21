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
import path
sys.path.insert(0, path.PATH_SHARE)

class Tradeup:
    def __init__(self):
        self.inputEntries: list[TradeupInputEntry] = list()
        self.outputEntries: list[TradeupOutputEntry] = list()
        self.favourite: bool = False
        self.dateFound: str = ""
        self.deviceUsed: str = ""
        self.tradeupCategory: int = 0
        self.tradeupGrade: int = 0
        self.averageInputFloat: float = 0.0
        self.adjustedAverageInputFloat: float = 0.0
        self.totalInputCost: float = 0.0
        self.totalOutputs: float = 0
        self.chanceToProfit: float = 0.0
        self.profitability: float = 0.0
        self.chanceToProfitSteamTax: float = 0.0
        self.profitabilitySteamTax: float = 0.0
        self.tradeupHash: str = ""

class TradeupInputEntry:
    def __init__(self):
        self.permID: int = 0
        self.weaponName: str = ""
        self.skinName: str = ""
        self.price: float = 0.0
        self.category: int = 0
        self.grade: int = 0
        self.wear: int = 0
        self.floatVal: float = 0.0
        self.adjustedFloatVal: float = 0.0

class TradeupOutputEntry:
    def __init__(self):
        self.permID: int = 0
        self.weaponName: str = ""
        self.skinName: str = ""
        self.price: float = 0.0
        self.category: int = 0
        self.grade: int = 0
        self.wear: int = 0
        self.floatVal: float = 0.0
        self.adjustedFloatVal: float = 0.0
        self.outputAmount: int = 0
        self.tradeupChance: float = 0.0
        self.moneyGain: float = 0.0
        self.moneyGainSteamTax: float = 0.0