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
from typing import Callable, Optional

from PyQt5 import sip
from PyQt5.QtGui import QIcon

from item import MarketItem
import path
sys.path.insert(0, path.PATH_SHARE)
import qt_resource
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QSize, Qt
import definitions
from tradeup_def import Tradeup

def createItemBoxPressable(item: MarketItem, callback: Callable[[MarketItem], None]) -> QWidget:
    itemBox = qt_resource.createWidget(f"itemBox{item.tempID}", QVBoxLayout(), Qt.AlignmentFlag.AlignTop)
    nameLabel = createItemNameLabel(item)
    buttonIcon = createItemButtonIcon(item, callback)
    nameCategoryWearLabel = createItemNameCategoryWearLabel(item)
    itemBox.layout().addWidget(nameLabel)
    itemBox.layout().addWidget(buttonIcon)
    itemBox.layout().addWidget(nameCategoryWearLabel)
    color = definitions.gradeToRGBString(item.grade)
    itemBoxSheet = f"""#{itemBox.objectName()} {{
        border: 1px solid;
        border-radius: 10px;
        border-color: rgb({color})
    }}"""
    itemBox.setStyleSheet(itemBoxSheet)
    return itemBox

def createItemButtonIcon(item: MarketItem, callback: Callable[[MarketItem], None]) -> QPushButton:
    color = definitions.gradeToRGBString(item.grade)
    buttonIconName = f"itemIcon{item.tempID}"
    buttonIconSheet = f"""#{buttonIconName} {{
        border: 1px solid;
        border-radius: 10px;
        border-color: rgb({color})
    }}"""
    buttonIcon = qt_resource.createButton(buttonIconName, "", qt_resource.fontSystemHudNormal, buttonIconSheet)
    buttonIcon.setIcon(QIcon(str(definitions.PATH_DIST_ASSETS / "unknown.png")))
    buttonIcon.setIconSize(QSize(128, 128))
    qt_resource.getSkinIcon(item, lambda icon: loadButtonFetchedIconCallback(buttonIcon, icon))
    buttonIcon.clicked.connect(lambda: callback(item))
    return buttonIcon

def loadButtonFetchedIconCallback(button: QPushButton, icon: QIcon):
    if sip.isdeleted(button): return
    button.setIcon(icon)
    button.setIconSize(QSize(128, 128))

def createItemNameLabel(item: MarketItem, alignment: Optional[Qt.AlignmentFlag] = None) -> QLabel:
    itemLabelName = qt_resource.createLabel(f"itemLabelName{item.tempID}", f"{item.weaponName} {item.skinName}", qt_resource.fontSystemHudNormal, alignment)
    return itemLabelName

def createItemNameCategoryWearLabel(item: MarketItem, alignment: Optional[Qt.AlignmentFlag] = None) -> QLabel:
    itemLabelWearCategory = qt_resource.createLabel(f"itemLabelCategoryWear{item.tempID}", f"{definitions.wearToString(item.wear)} | {definitions.categoryToString(item.category)}", qt_resource.fontSystemHudNormal, alignment)
    return itemLabelWearCategory

def createItemNameCategoryWearGradeLabel(item: MarketItem, alignment: Optional[Qt.AlignmentFlag] = None) -> QLabel:
    itemLabelWearCategory = qt_resource.createLabel(f"itemLabelCategoryWearGrade{item.tempID}", f"{definitions.wearToString(item.wear)} | {definitions.categoryToString(item.category)} | {definitions.gradeToString(item.grade)}", qt_resource.fontSystemHudNormal, alignment)
    return itemLabelWearCategory

def createItemMarketPriceLabel(item: MarketItem, alignment: Optional[Qt.AlignmentFlag] = None) -> QLabel:
    itemLabelPrice = qt_resource.createLabel(f"itemLabelPrice{item.tempID}", f"Market Price ${str(item.marketPrice)}", qt_resource.fontSystemHudNormal, alignment)
    return itemLabelPrice  

def createModifiedPriceLabel(item: MarketItem, alignment: Optional[Qt.AlignmentFlag] = None) -> QLabel:
    itemLabelPrice = qt_resource.createLabel(f"modifiedLabelPrice{item.tempID}", f"Modified Price ${str(item.modifiedPrice)}", qt_resource.fontSystemHudNormal, alignment)
    return itemLabelPrice  

def createItemCurrentPriceLabel(item: MarketItem, alignment: Optional[Qt.AlignmentFlag] = None) -> QLabel:
    itemLabelPrice = qt_resource.createLabel(f"currentLabelPrice{item.tempID}", f"Current Price ${str(item.price)}", qt_resource.fontSystemHudNormal, alignment)
    return itemLabelPrice  

def createItemSteamTaxPriceLabel(item: MarketItem, alignment: Optional[Qt.AlignmentFlag] = None) -> QLabel:
    itemLabelPrice = qt_resource.createLabel(f"priceLabelSteamTaxPrice{item.tempID}", f"Current Price Steam Tax ${str(item.priceSteamTax)}", qt_resource.fontSystemHudNormal, alignment)
    return itemLabelPrice

def createItemSteamMarketURLLabel(item: MarketItem, alignment: Optional[Qt.AlignmentFlag] = None) -> QLabel:
    itemSteamMarketURL = qt_resource.createLabel(f"steamMarketURL{item.tempID}", f"<a style='color:red;' href=\"{item.steamMarketUrl}\">Steam Market URL</a>", qt_resource.fontSystemHudNormal, alignment)
    itemSteamMarketURL.setTextFormat(Qt.TextFormat.RichText)
    itemSteamMarketURL.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    itemSteamMarketURL.setOpenExternalLinks(True)
    return itemSteamMarketURL  

def createTradeupDateTimeLabel(tradeup: Tradeup, alignment: Optional[Qt.AlignmentFlag] = None):
    dateTimeLabel = qt_resource.createLabel("dateTimeLabel", f"{tradeup.dateFound}", qt_resource.fontSystemHudNormal, alignment)
    return dateTimeLabel

def createProfitabilityLabel(tradeup: Tradeup, alignment: Optional[Qt.AlignmentFlag] = None):
    profLabel = qt_resource.createLabel("profitabilityLabel", f"Profitability {int(tradeup.profitability)}% - {int(tradeup.profitabilitySteamTax)}% TAX", qt_resource.fontSystemHudNormal, alignment)
    return profLabel

def createChanceToProfitLabel(tradeup: Tradeup, alignment: Optional[Qt.AlignmentFlag] = None):
    chanceToProfLabel = qt_resource.createLabel("chanceToProfitLabel", f"Profit Chance {int(tradeup.chanceToProfit)}% - {int(tradeup.chanceToProfitSteamTax)}% TAX", qt_resource.fontSystemHudNormal, alignment)
    return chanceToProfLabel

def createFloatValLabel(floatVal: float, alignment: Optional[Qt.AlignmentFlag] = None):
    chanceToProfLabel = qt_resource.createLabel("floatValLabel", f"Float Value {round(floatVal, 4)}", qt_resource.fontSystemHudNormal, alignment)
    return chanceToProfLabel

def createAdjustedFloatValLabel(floatVal: float, alignment: Optional[Qt.AlignmentFlag] = None):
    chanceToProfLabel = qt_resource.createLabel("adjustedFloatValLabel", f"Adjusted Float Value {round(floatVal, 4)}", qt_resource.fontSystemHudNormal, alignment)
    return chanceToProfLabel

def createEntryItemTradeupChanceLabel(tradeupChance: float, alignment: Optional[Qt.AlignmentFlag] = None):
    tradeupChanceLabel = qt_resource.createLabel("tradeupChanceLabel", f"Tradeup Chance {round(tradeupChance, 2)}%", qt_resource.fontSystemHudNormal, alignment)
    return tradeupChanceLabel

def createEntryItemMoneyGainLabel(moneyGain: float, moneyGainSteamTax: float, alignment: Optional[Qt.AlignmentFlag] = None):
    moneyGainLabel = qt_resource.createLabel("moneyGainLabel", f"Gain ${round(moneyGain, 2)} - ${round(moneyGainSteamTax, 2)} TAX", qt_resource.fontSystemHudNormal, alignment)
    return moneyGainLabel

def createInputPriceLabel(tradeup: Tradeup, alignment: Optional[Qt.AlignmentFlag] = None):
    inputPriceLabel = qt_resource.createLabel("inputPriceLabel", f"Input Price ${round(tradeup.totalInputCost, 3)}", qt_resource.fontSystemHudNormal, alignment)
    return inputPriceLabel 