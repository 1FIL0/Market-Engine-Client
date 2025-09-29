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

from io import BytesIO
import os
import sys

import requests
import path
import auth_server
sys.path.insert(0, path.PATH_SHARE)
from subprocess import Popen
from typing import Any, Optional, cast
import webbrowser
from item import MarketItem
from tradeup_def import Tradeup, TradeupInputEntry, TradeupOutputEntry
from PyQt5.QtWidgets import QCheckBox, QDoubleSpinBox, QGridLayout, QHBoxLayout, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, QTimer, Qt
from form_main_window import Ui_MainWindow
import definitions
import tradeup_memory
import shared_args
import proc
import file_handler
import qt_resource
from qt_stdout_worker import QTStdoutWorker
import widgets
import hardware
import item_memory
import logger

MARKET_ENGINE_VER = "1.0.1"

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # This sets up the UI elements from the .ui file  # pyright: ignore[reportUnknownMemberType]
        self.setMaximumSize(1300, 1200)
        self.setWindowTitle(f"Market Engine Client {MARKET_ENGINE_VER}")
        self.setWindowIcon(QIcon(str(definitions.PATH_DIST_ASSETS / "ui" / "market_engine_client_desktop.png")))
        self.initRefresher()
        self.initApp()

    def initRefresher(self):
        tradeup_memory.addTradeupsLoadedCallback(lambda: self.refreshManagerStats())
        tradeup_memory.addTradeupsLoadedCallback(lambda: self.refreshTradeupEntries())

    def initApp(self):
        self.initAccount()
        self.updateCenterStacked(0)
        self.initProcesses()
        self.initLeftTab()
        self.initSettings()
        self.initHome()
        self.initSonar()
        self.initTradeupEngine()
        self.initTradeupViewer()
        self.initItemLibrary()
        self.initHelp()

    def initProcesses(self):
        self.processSonar: Optional[Popen[str]] = None
        self.processCalculator: Optional[Popen[str]] = None
        self.processSonarSTDOutWorker: Optional[QTStdoutWorker] = None
        self.processTradeupEngineSTDOutWorker: Optional[QTStdoutWorker] = None

    def initLeftTab(self):
        self.buttonTabHome.clicked.connect(lambda: self.updateCenterStacked(0))
        self.buttonTabSonar.clicked.connect(lambda: self.updateCenterStacked(1))
        self.buttonTabTradeupEngine.clicked.connect(lambda: self.updateCenterStacked(2))
        self.buttonTabProfitableTradeups.clicked.connect(lambda: self.updateCenterStacked(3))
        self.buttonTabItemLibrary.clicked.connect(lambda: self.updateCenterStacked(4))
        self.buttonTabSettings.clicked.connect(lambda: self.updateCenterStacked(5))
        self.buttonTabAccount.clicked.connect(lambda: self.updateCenterStacked(6))
        self.buttonTabHelp.clicked.connect(lambda: self.updateCenterStacked(7))

    def updateCenterStacked(self, index: int):
        self.centralStacked.setCurrentIndex(index)
        match index:
            case 0: self.setWindowTitle(f"Home - Market Engine Client {MARKET_ENGINE_VER}")
            case 1: self.setWindowTitle(f"Sonar - Market Engine Client {MARKET_ENGINE_VER}")
            case 2: self.setWindowTitle(f"Tradeup Engine - Market Engine Client {MARKET_ENGINE_VER}")
            case 3: self.setWindowTitle(f"Tradeup Viewer - Market Engine Client {MARKET_ENGINE_VER}")
            case 4: self.setWindowTitle(f"Item Library - Market Engine Client {MARKET_ENGINE_VER}")
            case 5: self.setWindowTitle(f"Settings - Market Engine Client {MARKET_ENGINE_VER}")
            case 6: self.setWindowTitle(f"Account - Market Engine Client {MARKET_ENGINE_VER}")
            case 7: self.setWindowTitle(f"Help - Market Engine Client {MARKET_ENGINE_VER}")
            case _: pass

    # _____ HOME _____ #
    
    def initHome(self):
        item_memory.addReadyItemsLoadedCallback(lambda: self.itemsLoadedHome.setText(f"Items Loaded: {len(item_memory.getAllItems())}"))
        tradeup_memory.addTradeupsLoadedCallback(lambda: self.tradeupsFoundHome.setText(f"Tradeups Found: {len(tradeup_memory.getTradeups())}"))
        self.verLabel.setText(f"Version: {MARKET_ENGINE_VER}")
        self.buttonGoToWebsite.clicked.connect(lambda: self.openBrowserUrl(definitions.URL_MARKET_ENGINE))
        self.buttonGoToRepo.clicked.connect(lambda: self.openBrowserUrl(definitions.URL_MARKET_ENGINE_REPO))
        self.buttonCheckForUpdates.clicked.connect(lambda: self.openBrowserUrl(definitions.URL_MARKET_ENGINE_DOWNLOADS))
        self.buttonYoutube.clicked.connect(lambda: self.openBrowserUrl(definitions.URL_1FIL0_YOUTUBE))
        self.buttonDiscord.clicked.connect(lambda: self.openBrowserUrl(definitions.URL_1FIL0_DISCORD))
        self.buttonGithub.clicked.connect(lambda: self.openBrowserUrl(definitions.URL_MARKET_ENGINE_REPO))

    def openBrowserUrl(self, url: str):
        webbrowser.open(url)

    # _____ ACCOUNT _____ #

    def initAccount(self):
        self.loginThroughBrowser.clicked.connect(lambda: auth_server.openAuthorizationURL())
        self.updateAccount()
        auth_server.setUserAuthorizedCallback(self.handleAccountValidated)

    def handleAccountValidated(self):
        # Run on UI thread to not run on flask server thread
        QTimer.singleShot(0, self.updateAccount)

    def updateAccount(self):
        logger.sendMessage("Updating account information")
        authUserData = auth_server.getAuthUserData()
        if not authUserData: return
        self.labelLoggedInStatus.setText(f"Logged in as {authUserData.name}")
        self.apiAccessLabel.setText("API access granted")
        res = requests.get(authUserData.picture)
        imgData = BytesIO(res.content)
        accountPixmap = QPixmap()
        accountPixmap.loadFromData(imgData.read())
        self.accountIcon.setPixmap(accountPixmap)
        self.loginThroughBrowser.hide()

    # _____ SONAR _____ #

    def initSonar(self):
        self.buttonSonarExec.clicked.connect(lambda: self.execSonar())
        self.buttonSonarEnd.clicked.connect(lambda: self.killSonar())
        self.buttonSonarExecHome.clicked.connect(lambda: self.execSonar())
        self.buttonSonarEndHome.clicked.connect(lambda: self.killSonar())

    def execSonar(self):
        if self.processSonar != None: return
        cmdList: list[str] = []
        if shared_args.argDist == "dev":
            cmdList = [str(definitions.PYTHON_CMD_CLIENT), "-u", f"{definitions.PATH_DIST_CLIENT_SONAR_BINARY}", "--dist", shared_args.argDist]
        elif shared_args.argDist == "release":
            cmdList = [f"{definitions.PATH_DIST_CLIENT_SONAR_BINARY}", "--dist", shared_args.argDist]
        print(cmdList)
        self.processSonar = proc.runSubProcess(cmdList)
        self.sonarStatusStacked.setCurrentIndex(0)
        self.sonarStatusStackedHome.setCurrentIndex(0)
        self.processSonarSTDOutWorker = QTStdoutWorker(self.processSonar)
        self.processSonarSTDOutWorker.lineRead.connect(self.writeSonarOutput)
        self.processSonarSTDOutWorker.start()

    def killSonar(self):
        if self.processSonar == None: return
        proc.killSubProcess(self.processSonar)
        self.processSonar = None
        self.sonarStatusStacked.setCurrentIndex(1)
        self.sonarStatusStackedHome.setCurrentIndex(1)
        self.processSonarSTDOutWorker.stop()

    def writeSonarOutput(self, line: str):
        if len(self.sonarOutput.toPlainText()) > self.outputHistorySizeVal: self.sonarOutput.setText("")
        self.sonarOutput.append(line)

    # _____ COMPUTE CALCULATOR _____ #

    def initTradeupEngine(self):
        self.buttonTradeupEngineExec.clicked.connect(lambda: self.execTradeupEngine())
        self.buttonTradeupEngineEnd.clicked.connect(lambda: self.killTradeupEngine())
        self.buttonTradeupEngineExecHome.clicked.connect(lambda: self.execTradeupEngine())
        self.buttonTradeupEngineEndHome.clicked.connect(lambda: self.killTradeupEngine())

    def execTradeupEngine(self):
        if self.processCalculator != None: return
        cmdList = [f"{definitions.PATH_DIST_CLIENT_TRADEUP_ENGINE_BINARY}"]
        self.processCalculator = proc.runSubProcess(cmdList)
        self.tradeupEngineStatusStacked.setCurrentIndex(0)
        self.tradeupEngineStatusStackedHome.setCurrentIndex(0)
        self.processTradeupEngineSTDOutWorker = QTStdoutWorker(self.processCalculator)
        self.processTradeupEngineSTDOutWorker.lineRead.connect(self.writeTradeupEngineOutput)
        self.processTradeupEngineSTDOutWorker.start()
    
    def killTradeupEngine(self):
        if self.processCalculator == None: return
        proc.killSubProcess(self.processCalculator)
        self.processCalculator = None
        self.tradeupEngineStatusStacked.setCurrentIndex(1)
        self.tradeupEngineStatusStackedHome.setCurrentIndex(1)
        self.processTradeupEngineSTDOutWorker.stop()

    def writeTradeupEngineOutput(self, line: str):
        if len(self.tradeupEngineOutput.toPlainText()) > self.outputHistorySizeVal: self.tradeupEngineOutput.setText("")
        self.tradeupEngineOutput.append(line)

    # _____ TRADEUPS _____ #

    def initTradeupViewer(self):
        self.buttonBarViewManager.clicked.connect(lambda: self.stackedProfitableTradeups.setCurrentIndex(0))
        self.buttonBarViewEntries.clicked.connect(lambda: self.stackedProfitableTradeups.setCurrentIndex(1))
        self.buttonBarViewTradeup.clicked.connect(lambda: self.viewTradeupClicked())
        self.buttonTradeupViewOverview.clicked.connect(lambda: self.tradeupStacked.setCurrentIndex(0))
        self.buttonTradeupViewInputs.clicked.connect(lambda: self.tradeupStacked.setCurrentIndex(1))
        self.buttonTradeupViewOutputs.clicked.connect(lambda: self.tradeupStacked.setCurrentIndex(2))
        self.initTradeupManager()
        self.refreshTradeupEntries()

    def viewTradeupClicked(self):
        if self.tradeupInputsScrollContents.layout().count() == 0:
            self.stackedProfitableTradeups.setCurrentIndex(3)
        else:
            self.stackedProfitableTradeups.setCurrentIndex(2)

    def initTradeupManager(self):
        self.refreshManagerStats()
        self.buttonDeleteTradeups.clicked.connect(lambda: self.deleteTradeups())

    def refreshManagerStats(self):
        tradeups = tradeup_memory.getTradeups()
        self.totalTradeups.setText(f"{str(len(tradeups))}")

    def deleteTradeups(self):
        data: dict[str, Any] = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS))
        dataArray = data["DATA"]
        if self.selectEveryTradeup.isChecked():
            for tradeupEntry in dataArray[:]:
                if tradeupEntry["Favourite"] and not self.includeFavTradeups.isChecked():
                    continue
                dataArray.remove(tradeupEntry)
        else:
            for tradeupEntry in dataArray[:]:
                if tradeupEntry["Favourite"] and not self.includeFavTradeups.isChecked():
                    continue
                if self.profCheck.isChecked():
                    if tradeupEntry["Profitability"] > self.tradeupsProfMarginDelete.value():
                        continue
                if self.chanceToProfCheck.isChecked():
                    if tradeupEntry["Chance To Profit"] > self.tradeupsChanceToProfit.value():
                        continue
                dataArray.remove(tradeupEntry)
        file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS), data)

    def refreshTradeupEntries(self):
        self.setUpdatesEnabled(False)
        self.clearTradeupEntires()
        self.loadTradeupEntries()
        self.setUpdatesEnabled(True)

    def clearTradeupEntires(self):
        qt_resource.clearWidget(self.profitableTradeupsEntriesScrollContents)
    
    def clearTradeup(self):
        qt_resource.clearWidget(self.tradeupInputsScrollContents)
        qt_resource.clearWidget(self.tradeupOutputsScrollContents)

    def loadTradeupEntries(self):
        tradeups = tradeup_memory.getTradeups()
        itemsPerRow = 3
        sortedTradeups = sorted(tradeups, key=lambda t: not t.favourite)
        for index, tradeup in enumerate(sortedTradeups):
            tradeupBox = self.createTradeupEntryBox(tradeup)
            row: int = index // itemsPerRow
            col: int = index % itemsPerRow
            cast(QGridLayout, self.profitableTradeupsEntriesScrollContents.layout()).addWidget(tradeupBox, row, col)  

    def createTradeupEntrySelectButton(self, tradeup: Tradeup):
        color = definitions.gradeToRGBString(tradeup.tradeupGrade)
        buttonName = f"button{tradeup.tradeupHash}"
        buttonSheet = f"""#{buttonName} {{
            border: 1px solid;
            border-radius: 10px;
            border-color: rgb({color})
        }}"""
        buttonText = "Select"
        button = qt_resource.createButton(buttonName, buttonText, qt_resource.fontSystemHudNormal, buttonSheet)
        button.clicked.connect(lambda: self.loadTradeup(tradeup))
        return button

    def createTradeupEntryDeleteButton(self, tradeup: Tradeup):
        buttonName = f"delete{tradeup.tradeupHash}"
        button = qt_resource.createButton(buttonName, "", qt_resource.fontSystemHudNormal)
        icon = qt_resource.iconDelete
        button.setIcon(icon)
        button.setIconSize(QSize(20, 20))
        button.clicked.connect(lambda: self.deleteTradeup(tradeup))
        return button

    def createTradeupEntryFavButton(self, tradeup: Tradeup):
        buttonName = f"fav{tradeup.tradeupHash}"
        button = qt_resource.createButton(buttonName, "", qt_resource.fontSystemHudNormal)
        icon = qt_resource.iconFavDisabled
        if tradeup.favourite: icon = qt_resource.iconFavEnabled
        button.setIcon(icon)
        button.setIconSize(QSize(20, 20))
        button.clicked.connect(lambda: self.favouriteTradeup(tradeup))
        return button

    def deleteTradeup(self, tradeup: Tradeup):
        tradeup_memory.deleteTradeupFromFile(tradeup.tradeupHash)

    def favouriteTradeup(self, tradeup: Tradeup):
        val = True
        if tradeup.favourite: val = False
        tradeup_memory.favouriteTradeupInFile(tradeup.tradeupHash, val)
        
    def createTradeupEntryBox(self, tradeup: Tradeup):
        color = definitions.gradeToRGBString(tradeup.tradeupGrade)
        entryName = f"tradeup{tradeup.tradeupHash}"
        entrySheet = f"""#{entryName} {{
            border: 1px solid;
            border-radius: 10px;
            border-color: rgb({color})
        }}"""
        entryBox = qt_resource.createWidget(entryName, QVBoxLayout(), Qt.AlignTop, entrySheet)
        selectButton = self.createTradeupEntrySelectButton(tradeup)
        topButtons = qt_resource.createWidget("topbuttons", QHBoxLayout(), Qt.AlignTop)
        deleteButton = self.createTradeupEntryDeleteButton(tradeup)
        favButton = self.createTradeupEntryFavButton(tradeup)
        topButtons.layout().addWidget(deleteButton)
        topButtons.layout().addWidget(favButton)
        dateTimeLabel = widgets.createTradeupDateTimeLabel(tradeup)
        profitabilityLabel = widgets.createProfitabilityLabel(tradeup)
        chanceToProfLabel = widgets.createChanceToProfitLabel(tradeup)
        inputPriceLabel = widgets.createInputPriceLabel(tradeup)
        entryBox.layout().addWidget(topButtons)
        entryBox.layout().addWidget(dateTimeLabel)
        entryBox.layout().addWidget(profitabilityLabel)
        entryBox.layout().addWidget(chanceToProfLabel)
        entryBox.layout().addWidget(inputPriceLabel)
        entryBox.layout().addWidget(selectButton)
        return entryBox

    def createGeneralTradeupItemBox(self, name: str, item: MarketItem):
        color = definitions.gradeToRGBString(item.grade)
        boxSheet = f"""#{name}{{
            border: 1px solid;
            border-radius: 10px;
            border-color: rgb({color})
        }}
        """
        itemBox = qt_resource.createWidget(name, QHBoxLayout(), Qt.AlignTop, boxSheet)
        return itemBox

    def createTradeupItemBoxLeftContents(self, name: str, item: MarketItem):
        leftBox = qt_resource.createWidget(name, QVBoxLayout(), None, f"#{name}{{padding:0}}")
        buttonIcon = widgets.createItemButtonIcon(item, lambda item: None)
        buttonIcon.setMaximumSize(400, 200)
        itemNameLabel = widgets.createItemNameLabel(item)
        itemNameCategoryWearLabel = widgets.createItemNameCategoryWearLabel(item)
        leftBox.layout().addWidget(itemNameLabel)
        leftBox.layout().addWidget(buttonIcon)
        leftBox.layout().setAlignment(buttonIcon, Qt.AlignmentFlag.AlignLeft)
        leftBox.layout().addWidget(itemNameCategoryWearLabel)
        return leftBox

    def loadTradeup(self, tradeup: Tradeup):
        self.clearTradeup()
        self.loadTradeupOverview(tradeup)
        self.loadTradeupInputs(tradeup)
        self.loadTradeupOutputs(tradeup)

    def loadTradeupOverview(self, tradeup: Tradeup):
        self.favouriteTradeupCheckbox.setChecked(tradeup.favourite)
        self.favouriteTradeupCheckbox.stateChanged.connect(lambda: self.favouriteTradeup(tradeup))
        self.tradeupCategory.setText(f"{definitions.categoryToString(tradeup.tradeupCategory)}")
        self.tradeupGrade.setText(f"{definitions.gradeToString(tradeup.tradeupGrade)}")
        self.tradeupDeviceUsed.setText(f"{tradeup.deviceUsed}")
        self.tradeupOutputs.setText(f"{tradeup.totalOutputs}")
        self.tradeupDateFound.setText(f"{tradeup.dateFound}")
        self.tradeupProfitability.setText(f"{round(tradeup.profitability, 2)}% - {round(tradeup.profitabilitySteamTax)}% Steam Tax")
        self.tradeupChanceToProfit.setText(f"{round(tradeup.chanceToProfit, 2)}% - {round(tradeup.chanceToProfitSteamTax)}% Steam Tax")
        self.tradeupTotalInputCost.setText(f"${round(tradeup.totalInputCost, 3)}")
        self.tradeupAvgInputFloat.setText(f"{round(tradeup.averageInputFloat, 3)}")

    def loadTradeupInputs(self, tradeup: Tradeup):
        for index, inputItemEntry in enumerate(tradeup.inputEntries):
            inputItem: MarketItem = item_memory.getItemByPermId(inputItemEntry.permID)
            inputItemBox = self.createInputItemBox(inputItemEntry, inputItem, index)
            self.tradeupInputsScrollContents.layout().addWidget(inputItemBox)

    def createInputItemBox(self, inputItemEntry: TradeupInputEntry, inputItem: MarketItem, index: int):
        inputBoxName = f"input{index}"
        inputItemBox = self.createGeneralTradeupItemBox(inputBoxName, inputItem)
        inputLeftName = f"inputLeft{index}"
        leftBox = self.createTradeupItemBoxLeftContents(inputLeftName, inputItem)
        itemPriceLabel = widgets.createItemCurrentPriceLabel(inputItem)
        itemFloatValLabel = widgets.createFloatValLabel(inputItemEntry.floatVal)
        itemSteamMarketURLLabel = widgets.createItemSteamMarketURLLabel(inputItem)
        
        rightBox = self.createGeneralTradeupItemBox(f"inputRight{index}", inputItem)
        rightBoxContents = qt_resource.createWidget("inputRightContents", QVBoxLayout())
        rightBoxContents.layout().addWidget(itemPriceLabel)
        rightBoxContents.layout().addWidget(itemFloatValLabel)
        rightBoxContents.layout().addWidget(itemSteamMarketURLLabel)
        rightBox.layout().addWidget(rightBoxContents)
        inputItemBox.layout().addWidget(leftBox)
        inputItemBox.layout().addWidget(rightBox)
        return inputItemBox

    def loadTradeupOutputs(self, tradeup: Tradeup):
        for index, outputItemEntry in enumerate(tradeup.outputEntries):
            outputItem = item_memory.getItemByPermId(outputItemEntry.permID)
            outputItemBox = self.createOutputItemBox(tradeup, outputItemEntry, outputItem, index)
            self.tradeupOutputsScrollContents.layout().addWidget(outputItemBox)

    def createWinLoseIconEntry(self, tradeup: Tradeup, outputItem: MarketItem):
        labelIcon = QLabel()
        labelIcon.setFixedSize(25, 25)
        iconPath = ""
        if outputItem.price - tradeup.totalInputCost > 0.0:
            iconPath = os.path.join(definitions.PATH_DIST_ASSETS, "icons_market_engine", "win.png")
        else:
            iconPath = os.path.join(definitions.PATH_DIST_ASSETS, "icons_market_engine", "lose.png")
        pixmap = QPixmap(iconPath)
        pixmap = pixmap.scaled(25, 25)
        labelIcon.setPixmap(pixmap)
        labelIcon.setScaledContents(True)
        return labelIcon

    def createOutputItemBox(self, tradeup: Tradeup, outputItemEntry: TradeupOutputEntry, outputItem: MarketItem, index: int):
        outputBoxName = f"output{index}"
        outputItemBox = self.createGeneralTradeupItemBox(outputBoxName, outputItem)
        outputLeftName = f"outputLeft{index}"
        leftBox = self.createTradeupItemBoxLeftContents(outputLeftName, outputItem)
        itemPriceLabel = widgets.createItemCurrentPriceLabel(outputItem)
        itemFloatValLabel = widgets.createFloatValLabel(outputItemEntry.floatVal)
        itemTradeupChanceLabel = widgets.createEntryItemTradeupChanceLabel(outputItemEntry.tradeupChance)
        itemMoneyGainLabel = widgets.createEntryItemMoneyGainLabel(outputItemEntry.moneyGain, outputItemEntry.moneyGainSteamTax)
        itemSteamMarketURLLabel = widgets.createItemSteamMarketURLLabel(outputItem)
        
        winLoseIcon = self.createWinLoseIconEntry(tradeup, outputItem)
        rightBox = self.createGeneralTradeupItemBox(f"outputRight{index}", outputItem)
        rightBoxContents = qt_resource.createWidget("outputRightContents", QVBoxLayout(), None)
        rightBoxContents.layout().addWidget(winLoseIcon)
        rightBoxContents.layout().addWidget(itemPriceLabel)
        rightBoxContents.layout().addWidget(itemFloatValLabel)
        rightBoxContents.layout().addWidget(itemTradeupChanceLabel)
        rightBoxContents.layout().addWidget(itemMoneyGainLabel)
        rightBoxContents.layout().addWidget(itemSteamMarketURLLabel)
        rightBox.layout().addWidget(rightBoxContents)
        outputItemBox.layout().addWidget(leftBox)
        outputItemBox.layout().addWidget(rightBox)
        return outputItemBox

    # _____ ITEM LIBRARY _____ #

    def initItemLibrary(self):
        self.buttonLibrarySearchAll.clicked.connect(lambda: self.loadItemLibrary(self.getFilteredItemsAll()))
        self.buttonLibrarySearchConfig.clicked.connect(lambda: self.loadItemLibrary(self.getFilteredItemsConfig()))
        self.buttonItemLibraryViewAll.clicked.connect(lambda: self.itemLibraryStacked.setCurrentIndex(0))
        self.buttonItemLibraryViewModified.clicked.connect(lambda: self.itemLibraryStacked.setCurrentIndex(1))
        self.itemLibraryAllPrev.clicked.connect(lambda: self.setPreviousPageItemLibraryAll())
        self.itemLibraryAllNext.clicked.connect(lambda: self.setNextPageItemLibraryAll())
        self.itemLibraryModifiedPrev.clicked.connect(lambda: self.setPreviousPageItemLibraryModified())
        self.itemLibraryModifiedNext.clicked.connect(lambda: self.setNextPageItemLibraryModified())
        self.itemLibraryAllPage.valueChanged.connect(self.setItemLibraryAllPage)
        self.itemLibraryModifiedPage.valueChanged.connect(self.setItemLibraryModifiedPage)
        self.loadItemLibrary(self.getFilteredItemsAll())

    def loadItemLibrary(self, filteredItems: list[MarketItem]):
        self.totalAllPages = 0
        self.totalModifiedPages = 0
        self.currentAllTablePage = 0
        self.currentModifiedTablePage = 0
        self.maxItemLibraryItemsPerPage = 18
        self.currentAllTablePage = 0
        self.currentModifiedTablePage = 0
        self.setUpdatesEnabled(False)

        self.allTableFilteredItems = filteredItems
        self.modifiedTableFilteredItems = self.loadFilteredItemsModified(filteredItems)
        self.refreshAllItemsTable(self.allTableFilteredItems)
        self.refreshModifiedItemsTable(self.modifiedTableFilteredItems)
        self.setItemLibraryAllPage(0)
        self.setItemLibraryModifiedPage(0)
        
        self.setUpdatesEnabled(True)

    def getFilteredItemsConfig(self):
        config = file_handler.loadJson(str(definitions.PATH_CONFIG_CLIENT_ITEM_LIBRARY))
        collections = set(config["Filter Collections"])
        categories = set(config["Filter Categories"])
        grades = set(config["Filter Grades"])
        wears = set(config["Filter Wears"])
        allItems = item_memory.getAllItems()
        filteredItems = [
            item for item in allItems
            if item.collection in collections
            and item.category in categories
            and item.grade in grades
            and item.wear in wears
        ]
        searchText = self.librarySearchBar.text()
        filteredItems = item_memory.getItemsByName(filteredItems, searchText)
        self.sortFilteredItems(filteredItems)
        return filteredItems

    def getFilteredItemsAll(self):
        filteredItems = item_memory.getAllItems()
        searchText = self.librarySearchBar.text()
        filteredItems = item_memory.getItemsByName(filteredItems, searchText)
        self.sortFilteredItems(filteredItems)
        return filteredItems

    def loadFilteredItemsModified(self, filteredItems: list[MarketItem]):
        modifiedItemsData = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS))
        modifiedLookup = {
            item["Perm ID"]: item
            for item in modifiedItemsData["DATA"]
            if item["Use Modified State"]
        }
        finalFilteredItems = [
            item for item in filteredItems if item.permID in modifiedLookup
        ]
        self.sortFilteredItems(finalFilteredItems)
        return finalFilteredItems

    def sortFilteredItems(self, filteredItems: list[MarketItem]):
        grades: list[int] = list()
        for i in range(definitions.consts.GRADE_MAX): grades.append(i)
        gradeOrder = {grade: index for index, grade in enumerate(grades)}
        filteredItems.sort(key=lambda item: gradeOrder.get(item.grade, float('inf')))

    def refreshAllItemsTable(self, filteredItems: list[MarketItem]):
        self.currentAllItemIndex = 0
        self.totalAllPages = int(len(filteredItems) / self.maxItemLibraryItemsPerPage)
        self.itemLibraryAllPage.setValue(0)
        self.itemLibraryAllPage.setMaximum(self.totalAllPages)
        self.itemLibraryAllPage.setSuffix(f" / {str(self.totalAllPages)}")

    def refreshModifiedItemsTable(self, filteredItems: list[MarketItem]):
        self.currentModifiedItemIndex = 0
        self.totalModifiedPages = int(len(filteredItems) / self.maxItemLibraryItemsPerPage)
        self.itemLibraryModifiedPage.setValue(0)
        self.itemLibraryModifiedPage.setMaximum(self.totalModifiedPages)
        self.itemLibraryModifiedPage.setSuffix(f" / {str(self.totalModifiedPages)}")

    def setItemLibraryAllPage(self, page: int):
        if page < 0 or page > self.totalAllPages: 
            return
        self.currentAllTablePage = page
        self.itemLibraryAllPage.setValue(self.currentAllTablePage)
        self.loadAllItemPage()

    def setPreviousPageItemLibraryAll(self):
        self.setItemLibraryAllPage(self.currentAllTablePage - 1)

    def setNextPageItemLibraryAll(self):
        self.setItemLibraryAllPage(self.currentAllTablePage + 1)

    def loadAllItemPage(self):
        qt_resource.clearWidget(self.scrollItemLibraryAllContents)
        self.currentAllItemIndex = 0
        indexStart = (self.currentAllTablePage) * self.maxItemLibraryItemsPerPage
        indexEnd = (self.currentAllTablePage + 1) * self.maxItemLibraryItemsPerPage
        for i in range(indexStart, indexEnd):
            if (i >= len(self.allTableFilteredItems)):
                return
            self.addItemToLibraryTable(self.scrollItemLibraryAllContents, self.allTableFilteredItems[i], self.currentAllItemIndex)
            self.currentAllItemIndex += 1

    def setItemLibraryModifiedPage(self, page: int):
        if page < 0 or page > self.totalModifiedPages: 
            return
        self.currentModifiedTablePage = page
        self.itemLibraryModifiedPage.setValue(self.currentModifiedTablePage)
        self.loadModifiedItemPage()

    def setPreviousPageItemLibraryModified(self):
        self.setItemLibraryModifiedPage(self.currentModifiedTablePage - 1)

    def setNextPageItemLibraryModified(self):
        self.setItemLibraryModifiedPage(self.currentModifiedTablePage + 1)

    def loadModifiedItemPage(self):
        qt_resource.clearWidget(self.scrollItemLibraryModifiedContents)
        self.currentModifiedItemIndex = 0
        indexStart = (self.currentModifiedTablePage) * self.maxItemLibraryItemsPerPage
        indexEnd = (self.currentModifiedTablePage + 1) * self.maxItemLibraryItemsPerPage
        for i in range(indexStart, indexEnd):
            if (i >= len(self.modifiedTableFilteredItems)):
                return
            self.addItemToLibraryTable(self.scrollItemLibraryModifiedContents, self.modifiedTableFilteredItems[i], self.currentModifiedItemIndex)
            self.currentModifiedItemIndex += 1

    def addItemToLibraryTable(self, table: QWidget, pageItem: MarketItem, itemIndex: int):
        itemsPerRow = 3
        itemBox = widgets.createItemBoxPressable(pageItem, self.filteredItemButtonPressed)
        itemBox.setMinimumSize(350, 200)
        row = itemIndex // itemsPerRow
        col = itemIndex % itemsPerRow
        cast(QGridLayout, table.layout()).addWidget(itemBox, row, col)

    def filteredItemButtonPressed(self, filteredItem: MarketItem):
        self.clearItemLibraryBottomInfo()
        self.createItemLibraryBottomInfo(filteredItem)

    def clearItemLibraryBottomInfo(self):
        qt_resource.clearWidget(self.itemLibraryItemInfoBox)

    def createItemLibraryBottomInfo(self, filteredItem: MarketItem):
        leftSect = self.createItemLibraryBottomInfoLeftSect(filteredItem)
        centerSect = self.createItemLibraryBottomInfoCenterSect(filteredItem)
        rightSect = self.createItemLibraryBottomInfoRightSect(filteredItem)
        rightGroupedSect = qt_resource.createWidget(f"bottomInfoRightGrouped", QHBoxLayout(), Qt.AlignRight)
        rightGroupedSect.layout().addWidget(centerSect)
        rightGroupedSect.layout().addWidget(rightSect)
        self.itemLibraryItemInfoBox.layout().addWidget(leftSect)
        self.itemLibraryItemInfoBox.layout().addWidget(rightGroupedSect)

    def createItemLibraryBottomInfoLeftSect(self, filteredItem: MarketItem):
        leftSect = qt_resource.createWidget(f"bottomInfoLeft", QHBoxLayout(), Qt.AlignLeft)
        buttonIcon = widgets.createItemButtonIcon(filteredItem, lambda item: None)
        nameLabel = widgets.createItemNameLabel(filteredItem)
        nameWearCategoryGradeLabel = widgets.createItemNameCategoryWearGradeLabel(filteredItem)
        currentPriceLabel = widgets.createItemCurrentPriceLabel(filteredItem)
        steamUrl = widgets.createItemSteamMarketURLLabel(filteredItem)
        basicInfoBox = qt_resource.createWidget(f"bottomInfoBasicItemBox", QVBoxLayout(), Qt.AlignTop, "padding:0")
        basicInfoBox.layout().addWidget(nameLabel)
        basicInfoBox.layout().addWidget(nameWearCategoryGradeLabel)
        basicInfoBox.layout().addWidget(currentPriceLabel)
        basicInfoBox.layout().addWidget(steamUrl)
        leftSect.layout().addWidget(buttonIcon)
        leftSect.layout().addWidget(basicInfoBox)
        return leftSect

    def createItemLibraryBottomInfoCenterSect(self, filteredItem: MarketItem):
        centerSect = qt_resource.createWidget(f"itemInfoCenter", QVBoxLayout(), Qt.AlignmentFlag.AlignCenter)
        headerLabel = qt_resource.createLabel(f"itemHeaderCenter", "", qt_resource.fontSystemHudNormal, Qt.AlignCenter)
        if filteredItem.useModifiedState:
            headerLabel.setText("Modification Enabled")
        else:
            headerLabel.setText("Modification Disabled")
        enableButton = qt_resource.createButton("enableModified", "Enable", qt_resource.fontSystemHudNormal)
        disableButton = qt_resource.createButton("enableModified", "Disable", qt_resource.fontSystemHudNormal)
        enableButton.clicked.connect(lambda: self.setItemModificationState(filteredItem, True))
        disableButton.clicked.connect(lambda: self.setItemModificationState(filteredItem, False))
        centerSect.layout().addWidget(headerLabel)
        centerSect.layout().addWidget(enableButton)
        centerSect.layout().addWidget(disableButton)
        return centerSect

    def createItemLibraryBottomInfoRightSect(self, filteredItem: MarketItem):
        rightSect = qt_resource.createWidget(f"itemInfoRight", QVBoxLayout(), Qt.AlignRight, "")
        headerLabel = qt_resource.createLabel("itemHeaderRight", "Modified price", qt_resource.fontSystemHudNormal, Qt.AlignCenter)
        customPriceBox = qt_resource.createDoubleSpinBox(f"customSpinBox", "$", "", qt_resource.fontSystemHudNormal, 0.0, 10000.0)
        self.loadItemModificationValue(filteredItem, customPriceBox)
        buttonsBox = qt_resource.createWidget(f"itemButtonsBox", QHBoxLayout(), Qt.AlignCenter)
        saveButton = qt_resource.createButton(f"itemEnableButton", "Save", qt_resource.fontSystemHudNormal)
        discardButton = qt_resource.createButton(f"itemDisableButton", "Discard", qt_resource.fontSystemHudNormal)
        saveButton.clicked.connect(lambda: self.saveItemModificationValue(filteredItem, customPriceBox.value()))
        discardButton.clicked.connect(lambda: self.loadItemModificationValue(filteredItem, customPriceBox))
        rightSect.layout().addWidget(headerLabel)
        rightSect.layout().addWidget(customPriceBox)
        rightSect.layout().addWidget(buttonsBox)
        buttonsBox.layout().addWidget(saveButton)
        buttonsBox.layout().addWidget(discardButton)
        return rightSect

    def saveItemModificationValue(self, filteredItem: MarketItem, value: float):
        data = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS))
        for item in data["DATA"]:
            if item["Perm ID"] == filteredItem.permID:
                item["Modified Price"] = value
                filteredItem.modifiedPrice = value
                break
        file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS), data)
        self.switchFilteredItemPrice(filteredItem)
        self.reloadItemLibraryBottomBar(filteredItem)

    def loadItemModificationValue(self, filteredItem: MarketItem, modificationSpinBox: QDoubleSpinBox):
        data = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS))
        for item in data["DATA"]:
            if item["Perm ID"] == filteredItem.permID:
                modificationSpinBox.setValue(item["Modified Price"])
                break

    def setItemModificationState(self, filteredItem: MarketItem, state: bool):
        data = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS))
        for item in data["DATA"]:
            if item["Perm ID"] == filteredItem.permID:
                item["Use Modified State"] = state
        filteredItem.useModifiedState = state
        self.switchFilteredItemPrice(filteredItem)
        file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS), data)
        self.reloadItemLibraryBottomBar(filteredItem)
        
    def switchFilteredItemPrice(self, filteredItem: MarketItem):
        if filteredItem.useModifiedState:
            filteredItem.price = filteredItem.modifiedPrice
        else:
            filteredItem.price = filteredItem.marketPrice

    def reloadItemLibraryBottomBar(self, filteredItem: MarketItem):
        self.clearItemLibraryBottomInfo()
        self.createItemLibraryBottomInfo(filteredItem)

    # _____ HELP _____ #

    def initHelp(self):
        self.marketEngineDocsButton.clicked.connect(lambda: self.openBrowserUrl(definitions.URL_MARKET_ENGINE_DOCS))

    # _____ SETTINGS _____ #

    def initSettings(self):
        self.settingsButtonSonar.clicked.connect(lambda: self.settingsStacked.setCurrentIndex(0))
        self.settingsButtonTradeupEngine.clicked.connect(lambda: self.settingsStacked.setCurrentIndex(1))
        self.settingsButtonItemLibrary.clicked.connect(lambda: self.settingsStacked.setCurrentIndex(2))
        self.settingsButtonUI.clicked.connect(lambda: self.settingsStacked.setCurrentIndex(3))
        self.initSonarSettings()
        self.initTradeupEngineSettings()
        self.initItemLibrarySettings()
        self.initUISettings()
        self.loadSonarSettings()
        self.loadTradeupEngineSettings()
        self.loadItemLibrarySettings()
        self.loadUISettings()

    # _____ SETTINGS SONAR _____ #

    def initSonarSettings(self):
        pass

    def saveSonarSettings(self):
        pass

    def defaultSonarSettings(self):
        pass

    def loadSonarSettings(self):
        pass

    # _____ SETTINGS COMPUTE CALCULATOR _____ #

    def initTradeupEngineSettings(self):
        self.buttonTradeupEngineSettingsSave.clicked.connect(lambda: self.saveTradeupEngineSettings())
        self.buttonTradeupEngineSettingsDiscard.clicked.connect(lambda: self.loadTradeupEngineSettings())
        self.buttonTradeupEngineSettingsDefaults.clicked.connect(lambda: self.defaultTradeupEngineSettings())
        gpus = hardware.getDevices()
        self.gpuEnableBoxes: list[QCheckBox] = list()
        self.gpuLabels: list[QLabel] = list()
        for i in range(len(gpus)):
            gpu = gpus[i]
            gpuWidget = qt_resource.createWidget("gpuWidget" + str(i), QHBoxLayout(), Qt.AlignLeft)
            gpuLabel = qt_resource.createLabel("gpuLabel" + str(i), gpu.name, qt_resource.fontSystemHudNormal, Qt.AlignLeft)
            gpuEnableBox: QCheckBox = qt_resource.createCheckbox("gpuCheckbox" + str(i), "Enabled", qt_resource.fontSystemHudNormal, False)
            gpuWidget.layout().addWidget(gpuEnableBox)
            gpuWidget.layout().addWidget(gpuLabel)
            self.tradeupEngineSettingsGPUS.layout().addWidget(gpuWidget)
            self.gpuEnableBoxes.append(gpuEnableBox)
            self.gpuLabels.append(gpuLabel)
        self.computeModeBox.currentIndexChanged.connect(lambda: self.updateGPUSettingsVisibility())
        self.updateGPUSettingsVisibility()

        if file_handler.readFileLocked(str(definitions.PATH_CONFIG_CLIENT_TRADEUP_ENGINE)) == "{}": self.defaultTradeupEngineSettings()

    def updateGPUSettingsVisibility(self):
        if self.computeModeBox.currentIndex() == 1:
            self.tradeupEngineSettingsGPUS.show()
        else:
            self.tradeupEngineSettingsGPUS.hide()

    def saveTradeupEngineSettings(self):
        config: dict[str, Any] = {
            "Compute Rarities": [],
            "Compute Categories": [],
            "Single Item Batch": False,
            "Batch Size": 0,
            "Minimum Input Float": 0,
            "Maximum Input Float": 0,
            "Max Input Price": 0,
            "Profit Margin": 0,
            "Devices": [],
            "Max Tradeups In File": 0,
            "Output Verbose": True,
        }
        if self.tradeupEngineSettingsConsumer.isChecked(): config["Compute Rarities"].append(0)
        if self.tradeupEngineSettingsIndustrial.isChecked(): config["Compute Rarities"].append(1)
        if self.tradeupEngineSettingsMilspec.isChecked(): config["Compute Rarities"].append(2)
        if self.tradeupEngineSettingsRestricted.isChecked(): config["Compute Rarities"].append(3)
        if self.tradeupEngineSettingsClassified.isChecked(): config["Compute Rarities"].append(4)
        if self.tradeupEngineSettingsNormal.isChecked(): config["Compute Categories"].append(0)
        if self.tradeupEngineSettingsStatTrak.isChecked(): config["Compute Categories"].append(1)
        config["Single Item Batch"] = self.tradeupEngineSettingsSingleItemBatch.isChecked()
        config["Batch Size"] = self.tradeupEngineSettingsBatchSize.value()
        config["Minimum Input Float"] = self.tradeupEngineSettingsMinInputFloat.value()
        config["Maximum Input Float"] = self.tradeupEngineSettingsMaxInputFloat.value()
        config["Max Input Price"] = self.tradeupEngineSettingsMaxInputPrice.value()
        config["Profit Margin"] = self.tradeupEngineSettingsProfitMargin.value()
        config["Compute Mode"] = self.computeModeBox.currentIndex()
        for i in range(len(self.gpuLabels)):
            if self.gpuEnableBoxes[i].isChecked():
                config["Devices"].append(self.gpuLabels[i].text())
        config["Max Tradeups In File"] = self.tradeupEngineSettingsFileTradeupCapacity.value()
        config["Output Verbose"] = self.tradeupEngineSettingsOutputVerbose.isChecked()
        file_handler.replaceJsonDataAtomic(str(definitions.PATH_CONFIG_CLIENT_TRADEUP_ENGINE), config)

    def defaultTradeupEngineSettings(self):
        config = {
            "Compute Rarities": [0, 1, 2, 3, 4],
            "Compute Categories": [0, 1],
            "Single Item Batch": False,
            "Batch Size": 15,
            "Minimum Input Float": 35,
            "Maximum Input Float": 55,
            "Max Input Price": 10000,
            "Profit Margin": 120,
            "Compute Mode": 0,
            "Devices": [],
            "Max Tradeups In File": 75,
            "Output Verbose": True,
        }
        file_handler.replaceJsonDataAtomic(str(definitions.PATH_CONFIG_CLIENT_TRADEUP_ENGINE), config)
        self.loadTradeupEngineSettings()

    def loadTradeupEngineSettings(self):
        config = file_handler.loadJson(str(definitions.PATH_CONFIG_CLIENT_TRADEUP_ENGINE))
        for rarity in config["Compute Rarities"]:
            if rarity == 0: self.tradeupEngineSettingsConsumer.setChecked(True)
            if rarity == 1: self.tradeupEngineSettingsIndustrial.setChecked(True)
            if rarity == 2: self.tradeupEngineSettingsMilspec.setChecked(True)
            if rarity == 3: self.tradeupEngineSettingsRestricted.setChecked(True)
            if rarity == 4: self.tradeupEngineSettingsClassified.setChecked(True)
        for category in config["Compute Categories"]:
            if category == 0: self.tradeupEngineSettingsNormal.setChecked(True)
            if category == 1: self.tradeupEngineSettingsStatTrak.setChecked(True)
        self.tradeupEngineSettingsSingleItemBatch.setChecked(config["Single Item Batch"])
        self.tradeupEngineSettingsBatchSize.setValue(config["Batch Size"])
        self.tradeupEngineSettingsMinInputFloat.setValue(config["Minimum Input Float"])
        self.tradeupEngineSettingsMaxInputFloat.setValue(config["Maximum Input Float"])
        self.tradeupEngineSettingsMaxInputPrice.setValue(config["Max Input Price"])
        self.tradeupEngineSettingsProfitMargin.setValue(config["Profit Margin"])
        self.computeModeBox.setCurrentIndex(config["Compute Mode"])
        for i in range(len(self.gpuLabels)):
            self.gpuEnableBoxes[i].setChecked(False)
            for device in config["Devices"]:
                if self.gpuLabels[i].text() == device:
                    self.gpuEnableBoxes[i].setChecked(True)
        if len(self.gpuLabels) <= 0: self.noGpusFoundLabel.show()
        else: self.noGpusFoundLabel.hide()
        self.tradeupEngineSettingsFileTradeupCapacity.setValue(config["Max Tradeups In File"])
        self.tradeupEngineSettingsOutputVerbose.setChecked(config["Output Verbose"])

    # _____ SETTINGS ITEM LIBRARY _____ #

    def initItemLibrarySettings(self):
        self.buttonItemLibrarySettingsSave.clicked.connect(lambda: self.saveItemLibrarySettings())
        self.buttonItemLibrarySettingsDiscard.clicked.connect(lambda: self.loadItemLibrarySettings())
        self.buttonItemLibrarySettingsDefaults.clicked.connect(lambda: self.defaultItemLibrarySettings())
        self.outputHistorySizeVal: int = 0
        self.itemLibraryCollectionCheckboxes = [
            self.colAlpha, self.colAncient, self.colAnubis, self.colArmsDeal, self.colArmsDeal2, self.colArmsDeal3, self.colAscent, self.colAssault, self.colBaggage, 
            self.colBank, self.colBlacksite, self.colBoreal, self.colBravo, self.colBreakout, self.colBrokenFang, self.colCS20, self.colCache, self.colCanals, self.colChopShop, self.colChroma, 
            self.colChroma2, self.colChroma3, self.colClutch, self.colCobblestone, self.colControl, self.colDangerZone, self.colDreamsAndNightmares, self.colDust, self.colDust2, self.colDust22021, 
            self.colEsports2013, self.colEsports2013winter, self.colEsports2014summer, self.colFalchion, self.colFever, self.colFracture, self.colGallery, self.colGamma, self.colGamma2, self.colGlove, 
            self.colGodsAndMonsters, self.colGraphicDesign, self.colHavoc, self.colHorizon, self.colHuntsman, self.colHydra, self.colInferno, self.colInferno2018, self.colItaly, self.colKilowatt, 
            self.colLake, self.colLimitedEditionItem, self.colMilitia, self.colMirage, self.colMirage2021, self.colNorse, self.colNuke, self.colNuke2018, self.colOffice, self.colOverpass, self.colOverpass2024, 
            self.colPhoenix, self.colPrisma, self.colPrisma2, self.colRadiant, self.colRecoil, self.colRevolution, self.colRevolverCase, self.colRiptide, self.colRisingSun, self.colSafehouse, self.colShadow, 
            self.colShatteredWeb, self.colSnakebite, self.colSpectrum, self.colSpectrum2, self.colSportAndField, self.colStMarc, self.colTrain, self.colTrain2021, self.colTrain2025, self.colVanguard, self.colVertigo, 
            self.colVertigo2021, self.colWildfire, self.colWinterOffensive, self.colXRay
        ]
        self.buttonItemLibraryCheckAllCollections.clicked.connect(lambda: self.itemLibraryCheckAllCollections(True))
        self.buttonItemLibraryUncheckAllCollections.clicked.connect(lambda: self.itemLibraryCheckAllCollections(False))
        if file_handler.readFileLocked(str(definitions.PATH_CONFIG_CLIENT_ITEM_LIBRARY)) == "{}": self.defaultItemLibrarySettings()

    def itemLibraryCheckAllCollections(self, val: bool):
        for checkbox in self.itemLibraryCollectionCheckboxes:
            checkbox.setChecked(val)

    def saveItemLibrarySettings(self):
        config: dict[str, Any] = {
            "Filter Grades": [],
            "Filter Categories": [],
            "Filter Wears": [],
            "Filter Collections": [],
            "Sorting": 0
        }
        if self.itemLibraryGradeConsumer.isChecked(): config["Filter Grades"].append(0)
        if self.itemLibraryGradeIndustrial.isChecked(): config["Filter Grades"].append(1)
        if self.itemLibraryGradeMilspec.isChecked(): config["Filter Grades"].append(2)
        if self.itemLibraryGradeRestricted.isChecked(): config["Filter Grades"].append(3)
        if self.itemLibraryGradeClassified.isChecked(): config["Filter Grades"].append(4)
        if self.itemLibraryGradeCovert.isChecked(): config["Filter Grades"].append(5)
        if self.itemLibraryGradeContraband.isChecked(): config["Filter Grades"].append(6)
        if self.itemLibraryCategoryNormal.isChecked(): config["Filter Categories"].append(0)
        if self.itemLibraryCategoryStatTrak.isChecked(): config["Filter Categories"].append(1)
        if self.itemLibraryCategorySouvenir.isChecked(): config["Filter Categories"].append(2)
        if self.itemLibraryWearFN.isChecked(): config["Filter Wears"].append(0)
        if self.itemLibraryWearMM.isChecked(): config["Filter Wears"].append(1)
        if self.itemLibraryWearFT.isChecked(): config["Filter Wears"].append(2)
        if self.itemLibraryWearWW.isChecked(): config["Filter Wears"].append(3)
        if self.itemLibraryWearBS.isChecked(): config["Filter Wears"].append(4)
        if self.colAlpha.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ALPHA)  
        if self.colAncient.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ANCIENT)  
        if self.colAnubis.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ANUBIS)  
        if self.colArmsDeal.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ARMS_DEAL)  
        if self.colArmsDeal2.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ARMS_DEAL_2)  
        if self.colArmsDeal3.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ARMS_DEAL_3)  
        if self.colAscent.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ASCENT)  
        if self.colAssault.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ASSAULT)  
        if self.colBaggage.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_BAGGAGE)  
        if self.colBank.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_BANK)  
        if self.colBlacksite.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_BLACKSITE)  
        if self.colBoreal.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_BOREAL)  
        if self.colBravo.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_BRAVO)  
        if self.colBreakout.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_BREAKOUT)  
        if self.colBrokenFang.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_BROKEN_FANG)  
        if self.colCS20.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_CS20)  
        if self.colCache.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_CACHE)  
        if self.colCanals.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_CANALS)  
        if self.colChopShop.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_CHOP_SHOP)  
        if self.colChroma.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_CHROMA)  
        if self.colChroma2.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_CHROMA2)  
        if self.colChroma3.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_CHROMA3)  
        if self.colClutch.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_CLUTCH)  
        if self.colCobblestone.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_COBBLESTONE)  
        if self.colControl.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_CONTROL)  
        if self.colDangerZone.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_DANGER_ZONE)  
        if self.colDreamsAndNightmares.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_DREAMS_AND_NIGHTMARES)
        if self.colDust.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_DUST)  
        if self.colDust2.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_DUST2)  
        if self.colDust22021.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_DUST2_2021)  
        if self.colEsports2013.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ESPORTS_2013)  
        if self.colEsports2013winter.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ESPORTS_2013_WINTER)  
        if self.colEsports2014summer.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ESPORTS_2014_SUMMER)  
        if self.colFalchion.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_FALCHION)  
        if self.colFever.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_FEVER)  
        if self.colFracture.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_FRACTURE)  
        if self.colGallery.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_GALLERY)  
        if self.colGamma.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_GAMMA)  
        if self.colGamma2.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_GAMMA2)  
        if self.colGlove.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_GLOVE)  
        if self.colGodsAndMonsters.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_GODS_AND_MONSTERS)  
        if self.colGraphicDesign.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_GRAPHIC_DESIGN)  
        if self.colHavoc.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_HAVOC)  
        if self.colHorizon.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_HORIZON)  
        if self.colHuntsman.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_HUNTSMAN)  
        if self.colHydra.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_HYDRA)  
        if self.colInferno.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_INFERNO)  
        if self.colInferno2018.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_INFERNO_2018)  
        if self.colItaly.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ITALY)  
        if self.colKilowatt.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_KILOWATT)  
        if self.colLake.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_LAKE)  
        if self.colLimitedEditionItem.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_LIMITED_EDITION_ITEM)  
        if self.colMilitia.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_MILITIA)
        if self.colMirage.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_MIRAGE)  
        if self.colMirage2021.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_MIRAGE_2021)  
        if self.colNorse.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_NORSE)  
        if self.colNuke.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_NUKE)  
        if self.colNuke2018.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_NUKE_2018)  
        if self.colOffice.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_OFFICE)  
        if self.colOverpass.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_OVERPASS)  
        if self.colOverpass2024.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_OVERPASS_2024)  
        if self.colPhoenix.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_PHEONIX)  
        if self.colPrisma.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_PRISMA)  
        if self.colPrisma2.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_PRISMA2)  
        if self.colRadiant.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_RADIANT)  
        if self.colRecoil.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_RECOIL)  
        if self.colRevolution.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_REVOLUTION)  
        if self.colRevolverCase.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_REVOLVER_CASE)  
        if self.colRiptide.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_RIPTIDE)  
        if self.colRisingSun.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_RISING_SUN)  
        if self.colSafehouse.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_SAFEHOUSE)  
        if self.colShadow.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_SHADOW)  
        if self.colShatteredWeb.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_SHATTERED_WEB)  
        if self.colSnakebite.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_SNAKEBITE)  
        if self.colSpectrum.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_SPECTRUM)  
        if self.colSpectrum2.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_SPECTRUM_2)  
        if self.colSportAndField.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_SPORT_AND_FIELD)  
        if self.colStMarc.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_ST_MARC)  
        if self.colTrain.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_TRAIN)  
        if self.colTrain2021.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_TRAIN_2021)  
        if self.colTrain2025.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_TRAIN_2025)  
        if self.colVanguard.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_VANGUARD)  
        if self.colVertigo.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_VERTIGO)  
        if self.colVertigo2021.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_VERTIGO_2021)  
        if self.colWildfire.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_WILDFIRE)  
        if self.colWinterOffensive.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_WINTER_OFFENSIVE)  
        if self.colXRay.isChecked(): config["Filter Collections"].append(definitions.consts.COLLECTION_XRAY)
        file_handler.replaceJsonDataAtomic(str(definitions.PATH_CONFIG_CLIENT_ITEM_LIBRARY), config)

    def defaultItemLibrarySettings(self):
        config = {
            "Filter Grades": [
                0, 1, 2, 3, 4, 5, 6
            ],
            "Filter Categories": [
                0, 1, 2
            ],
            "Filter Wears": [
                0, 1, 2, 3, 4
            ],
            "Filter Collections": [

            ],
        }
        for collection in range(definitions.consts.COLLECTION_MAX):
            config["Filter Collections"].append(collection)

        file_handler.replaceJsonDataAtomic(str(definitions.PATH_CONFIG_CLIENT_ITEM_LIBRARY), config)
        self.loadItemLibrarySettings()

    def loadItemLibrarySettings(self):
        config = file_handler.loadJson(str(definitions.PATH_CONFIG_CLIENT_ITEM_LIBRARY))
        for grade in config["Filter Grades"]:
            if grade == 0: self.itemLibraryGradeConsumer.setChecked(True)
            if grade == 1: self.itemLibraryGradeIndustrial.setChecked(True)
            if grade == 2: self.itemLibraryGradeMilspec.setChecked(True)
            if grade == 3: self.itemLibraryGradeRestricted.setChecked(True)
            if grade == 4: self.itemLibraryGradeClassified.setChecked(True)
            if grade == 5: self.itemLibraryGradeCovert.setChecked(True)
            if grade == 6: self.itemLibraryGradeContraband.setChecked(True)
        for category in config["Filter Categories"]:
            if category == 0: self.itemLibraryCategoryNormal.setChecked(True)
            if category == 1: self.itemLibraryCategoryStatTrak.setChecked(True)
            if category == 2: self.itemLibraryCategorySouvenir.setChecked(True)
        for wear in config["Filter Wears"]:
            if wear == 0: self.itemLibraryWearFN.setChecked(True)
            if wear == 1: self.itemLibraryWearMM.setChecked(True)
            if wear == 2: self.itemLibraryWearFT.setChecked(True)
            if wear == 3: self.itemLibraryWearWW.setChecked(True)
            if wear == 4: self.itemLibraryWearBS.setChecked(True)
        for collection in config["Filter Collections"]:
            if collection == definitions.consts.COLLECTION_ALPHA: self.colAlpha.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ANCIENT: self.colAncient.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ANUBIS: self.colAnubis.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ARMS_DEAL: self.colArmsDeal.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ARMS_DEAL_2: self.colArmsDeal2.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ARMS_DEAL_3: self.colArmsDeal3.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ASCENT: self.colAscent.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ASSAULT: self.colAssault.setChecked(True)  
            if collection == definitions.consts.COLLECTION_BAGGAGE: self.colBaggage.setChecked(True)  
            if collection == definitions.consts.COLLECTION_BANK: self.colBank.setChecked(True)  
            if collection == definitions.consts.COLLECTION_BLACKSITE: self.colBlacksite.setChecked(True)  
            if collection == definitions.consts.COLLECTION_BOREAL: self.colBoreal.setChecked(True)  
            if collection == definitions.consts.COLLECTION_BRAVO: self.colBravo.setChecked(True)  
            if collection == definitions.consts.COLLECTION_BREAKOUT: self.colBreakout.setChecked(True)  
            if collection == definitions.consts.COLLECTION_BROKEN_FANG: self.colBrokenFang.setChecked(True)  
            if collection == definitions.consts.COLLECTION_CS20: self.colCS20.setChecked(True)  
            if collection == definitions.consts.COLLECTION_CACHE: self.colCache.setChecked(True)  
            if collection == definitions.consts.COLLECTION_CANALS: self.colCanals.setChecked(True)  
            if collection == definitions.consts.COLLECTION_CHOP_SHOP: self.colChopShop.setChecked(True)  
            if collection == definitions.consts.COLLECTION_CHROMA: self.colChroma.setChecked(True)  
            if collection == definitions.consts.COLLECTION_CHROMA2: self.colChroma2.setChecked(True)  
            if collection == definitions.consts.COLLECTION_CHROMA3: self.colChroma3.setChecked(True)  
            if collection == definitions.consts.COLLECTION_CLUTCH: self.colClutch.setChecked(True)  
            if collection == definitions.consts.COLLECTION_COBBLESTONE: self.colCobblestone.setChecked(True)  
            if collection == definitions.consts.COLLECTION_CONTROL: self.colControl.setChecked(True)  
            if collection == definitions.consts.COLLECTION_DANGER_ZONE: self.colDangerZone.setChecked(True)  
            if collection == definitions.consts.COLLECTION_DREAMS_AND_NIGHTMARES: self.colDreamsAndNightmares.setChecked(True)
            if collection == definitions.consts.COLLECTION_DUST: self.colDust.setChecked(True)  
            if collection == definitions.consts.COLLECTION_DUST2: self.colDust2.setChecked(True)  
            if collection == definitions.consts.COLLECTION_DUST2_2021: self.colDust22021.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ESPORTS_2013: self.colEsports2013.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ESPORTS_2013_WINTER: self.colEsports2013winter.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ESPORTS_2014_SUMMER: self.colEsports2014summer.setChecked(True)  
            if collection == definitions.consts.COLLECTION_FALCHION: self.colFalchion.setChecked(True)  
            if collection == definitions.consts.COLLECTION_FEVER: self.colFever.setChecked(True)  
            if collection == definitions.consts.COLLECTION_FRACTURE: self.colFracture.setChecked(True)  
            if collection == definitions.consts.COLLECTION_GALLERY: self.colGallery.setChecked(True)  
            if collection == definitions.consts.COLLECTION_GAMMA: self.colGamma.setChecked(True)  
            if collection == definitions.consts.COLLECTION_GAMMA2: self.colGamma2.setChecked(True)  
            if collection == definitions.consts.COLLECTION_GLOVE: self.colGlove.setChecked(True)  
            if collection == definitions.consts.COLLECTION_GODS_AND_MONSTERS: self.colGodsAndMonsters.setChecked(True)  
            if collection == definitions.consts.COLLECTION_GRAPHIC_DESIGN: self.colGraphicDesign.setChecked(True)  
            if collection == definitions.consts.COLLECTION_HAVOC: self.colHavoc.setChecked(True)  
            if collection == definitions.consts.COLLECTION_HORIZON: self.colHorizon.setChecked(True)  
            if collection == definitions.consts.COLLECTION_HUNTSMAN: self.colHuntsman.setChecked(True)  
            if collection == definitions.consts.COLLECTION_HYDRA: self.colHydra.setChecked(True)  
            if collection == definitions.consts.COLLECTION_INFERNO: self.colInferno.setChecked(True)  
            if collection == definitions.consts.COLLECTION_INFERNO_2018: self.colInferno2018.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ITALY: self.colItaly.setChecked(True)  
            if collection == definitions.consts.COLLECTION_KILOWATT: self.colKilowatt.setChecked(True)  
            if collection == definitions.consts.COLLECTION_LAKE: self.colLake.setChecked(True)  
            if collection == definitions.consts.COLLECTION_LIMITED_EDITION_ITEM: self.colLimitedEditionItem.setChecked(True)  
            if collection == definitions.consts.COLLECTION_MILITIA: self.colMilitia.setChecked(True)
            if collection == definitions.consts.COLLECTION_MIRAGE: self.colMirage.setChecked(True)  
            if collection == definitions.consts.COLLECTION_MIRAGE_2021: self.colMirage2021.setChecked(True)  
            if collection == definitions.consts.COLLECTION_NORSE: self.colNorse.setChecked(True)  
            if collection == definitions.consts.COLLECTION_NUKE: self.colNuke.setChecked(True)  
            if collection == definitions.consts.COLLECTION_NUKE_2018: self.colNuke2018.setChecked(True)  
            if collection == definitions.consts.COLLECTION_OFFICE: self.colOffice.setChecked(True)  
            if collection == definitions.consts.COLLECTION_OVERPASS: self.colOverpass.setChecked(True)  
            if collection == definitions.consts.COLLECTION_OVERPASS_2024: self.colOverpass2024.setChecked(True)  
            if collection == definitions.consts.COLLECTION_PHEONIX: self.colPhoenix.setChecked(True)  
            if collection == definitions.consts.COLLECTION_PRISMA: self.colPrisma.setChecked(True)  
            if collection == definitions.consts.COLLECTION_PRISMA2: self.colPrisma2.setChecked(True)  
            if collection == definitions.consts.COLLECTION_RADIANT: self.colRadiant.setChecked(True)  
            if collection == definitions.consts.COLLECTION_RECOIL: self.colRecoil.setChecked(True)  
            if collection == definitions.consts.COLLECTION_REVOLUTION: self.colRevolution.setChecked(True)  
            if collection == definitions.consts.COLLECTION_REVOLVER_CASE: self.colRevolverCase.setChecked(True)  
            if collection == definitions.consts.COLLECTION_RIPTIDE: self.colRiptide.setChecked(True)  
            if collection == definitions.consts.COLLECTION_RISING_SUN: self.colRisingSun.setChecked(True)  
            if collection == definitions.consts.COLLECTION_SAFEHOUSE: self.colSafehouse.setChecked(True)  
            if collection == definitions.consts.COLLECTION_SHADOW: self.colShadow.setChecked(True)  
            if collection == definitions.consts.COLLECTION_SHATTERED_WEB: self.colShatteredWeb.setChecked(True)  
            if collection == definitions.consts.COLLECTION_SNAKEBITE: self.colSnakebite.setChecked(True)  
            if collection == definitions.consts.COLLECTION_SPECTRUM: self.colSpectrum.setChecked(True)  
            if collection == definitions.consts.COLLECTION_SPECTRUM_2: self.colSpectrum2.setChecked(True)  
            if collection == definitions.consts.COLLECTION_SPORT_AND_FIELD: self.colSportAndField.setChecked(True)  
            if collection == definitions.consts.COLLECTION_ST_MARC: self.colStMarc.setChecked(True)  
            if collection == definitions.consts.COLLECTION_TRAIN: self.colTrain.setChecked(True)  
            if collection == definitions.consts.COLLECTION_TRAIN_2021: self.colTrain2021.setChecked(True)  
            if collection == definitions.consts.COLLECTION_TRAIN_2025: self.colTrain2025.setChecked(True)  
            if collection == definitions.consts.COLLECTION_VANGUARD: self.colVanguard.setChecked(True)  
            if collection == definitions.consts.COLLECTION_VERTIGO: self.colVertigo.setChecked(True)  
            if collection == definitions.consts.COLLECTION_VERTIGO_2021: self.colVertigo2021.setChecked(True)  
            if collection == definitions.consts.COLLECTION_WILDFIRE: self.colWildfire.setChecked(True)  
            if collection == definitions.consts.COLLECTION_WINTER_OFFENSIVE: self.colWinterOffensive.setChecked(True)  
            if collection == definitions.consts.COLLECTION_XRAY: self.colXRay.setChecked(True)

    # _____ SETTINGS UI _____ #

    def initUISettings(self):
        self.buttonUISettingsSave.clicked.connect(lambda: self.saveUISettings())
        self.buttonUISettingsDiscard.clicked.connect(lambda: self.loadUISettings())
        self.buttonUISettingsDefaults.clicked.connect(lambda: self.defaultUISettings())
        self.outputHistorySizeVal = 0
        if file_handler.readFileLocked(str(definitions.PATH_CONFIG_CLIENT_UI)) == "{}": self.defaultUISettings()

    def saveUISettings(self):
        config = {
            "Theme": 0,
            "Output History Size": 100000,
        }
        config["Theme"] = self.uiTheme.currentIndex()
        config["Output History Size"] = self.outputHistorySize.value()
        file_handler.replaceJsonDataAtomic(str(definitions.PATH_CONFIG_CLIENT_UI), config)

    def defaultUISettings(self):
        config = {
            "Theme": 0,
            "Output History Size": 100000,
        }
        file_handler.replaceJsonDataAtomic(str(definitions.PATH_CONFIG_CLIENT_UI), config)
        self.loadUISettings()

    def loadUISettings(self):
        config = file_handler.loadJson(str(definitions.PATH_CONFIG_CLIENT_UI))
        self.uiTheme.setCurrentIndex(config["Theme"])
        self.outputHistorySize.setValue(config["Output History Size"])
        self.outputHistorySizeVal = config["Output History Size"]
        
