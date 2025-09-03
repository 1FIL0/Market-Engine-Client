# FILE WATCHER MANAGER

import sys
import path
sys.path.insert(0, path.PATH_SHARE)
import item_memory
import definitions
import logger
import tradeup_memory
from time import perf_counter
from qt_fwatcher_worker import QTFWatcherWorker 
from PyQt5.QtCore import QThread

fWatcherWorkers: list[QTFWatcherWorker] = list()
fWatcherThreads: list[QThread] = list()

def init():
    global fWatcherWorkers
    global fWatcherThreads
    readyItemsFWatcher = QTFWatcherWorker(str(definitions.PATH_DATA_CLIENT_READY_ITEMS), 0.01, 0.1, handleReadyItemsUpdate)
    modifiedItemsFWatcher = QTFWatcherWorker(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS), 0.01, 0.1, handleModifiedItemsUpdate)
    tradeupsFWatcher = QTFWatcherWorker(str(definitions.PATH_DATA_CLIENT_PROFITABLE_TRADEUPS), 0.01, 0.1, handleTradeupsUpdate)

    readyItemsFWatcherThread = QThread()
    modifiedFWatcherThread = QThread()
    tradeupsFWatcherThread = QThread()

    readyItemsFWatcherThread.started.connect(readyItemsFWatcher.start)
    modifiedFWatcherThread.started.connect(modifiedItemsFWatcher.start)
    tradeupsFWatcherThread.started.connect(tradeupsFWatcher.start)

    readyItemsFWatcher.moveToThread(readyItemsFWatcherThread)
    modifiedItemsFWatcher.moveToThread(modifiedFWatcherThread)
    tradeupsFWatcher.moveToThread(tradeupsFWatcherThread)

    fWatcherWorkers.append(readyItemsFWatcher)
    fWatcherWorkers.append(modifiedItemsFWatcher)
    fWatcherWorkers.append(tradeupsFWatcher)
    fWatcherThreads.append(readyItemsFWatcherThread)
    fWatcherThreads.append(modifiedFWatcherThread)
    fWatcherThreads.append(tradeupsFWatcherThread)
    
    readyItemsFWatcherThread.start()
    modifiedFWatcherThread.start()
    tradeupsFWatcherThread.start()

def handleReadyItemsUpdate():
    startTime = perf_counter()
    item_memory.loadItems()
    endTime = perf_counter()
    logger.sendMessage(f"Ready Items Refreshed in {endTime - startTime:.4f} seconds")
    handleTradeupsUpdate()

def handleModifiedItemsUpdate():
    startTime = perf_counter()
    tradeup_memory.loadTradeups()
    endTime = perf_counter()
    logger.sendMessage(f"Modified Items Refreshed in {endTime - startTime:.4f} seconds")
    handleReadyItemsUpdate()

def handleTradeupsUpdate():
    startTime = perf_counter()
    tradeup_memory.recalculateTradeupsFile()
    tradeup_memory.loadTradeups()
    endTime = perf_counter()
    logger.sendMessage(f"Tradeups Refreshed in {endTime - startTime:.4f} seconds")
