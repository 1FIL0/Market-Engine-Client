# FILE WATCHER MANAGER

import sys
from typing import Optional
import path
sys.path.insert(0, path.PATH_SHARE)
import item_memory
import definitions
import logger
import tradeup_memory
from time import perf_counter
from qt_fwatcher_worker import QTFWatcherWorker 
from PyQt5.QtCore import QThread

INDEX_FWATCHER_READY_ITEMS = 0
INDEX_FWATCHER_MODIFIED_ITEMS = 1
INDEX_FWATCHER_TRADEUPS = 2

fWatcherWorkers: list[Optional[QTFWatcherWorker]] = [None, None, None]
fWatcherThreads: list[Optional[QThread]] = [None, None, None]

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

    fWatcherWorkers[INDEX_FWATCHER_READY_ITEMS] = readyItemsFWatcher
    fWatcherWorkers[INDEX_FWATCHER_MODIFIED_ITEMS] = modifiedItemsFWatcher
    fWatcherWorkers[INDEX_FWATCHER_TRADEUPS] = tradeupsFWatcher
    fWatcherThreads[INDEX_FWATCHER_READY_ITEMS] = readyItemsFWatcherThread
    fWatcherThreads[INDEX_FWATCHER_MODIFIED_ITEMS] = modifiedFWatcherThread
    fWatcherThreads[INDEX_FWATCHER_TRADEUPS] = tradeupsFWatcherThread
    
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
