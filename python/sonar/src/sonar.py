import sys
from typing import Any
import path
sys.path.insert(0, path.PATH_SHARE)
import requests
import time
import definitions
import user_auth
import logger
import file_handler

sleepMin = 1
gModifiedItemsData: dict[str, Any] = {}
gModifiedLookup: dict[str, Any] = {}

def beginScanLoop() -> None:
    global gModifiedItemsData
    global gModifiedLookup
    while (1):
        requestReadyItems()
        logger.sendMessage(f"Finished -> Next scan in {sleepMin} minutes") 
        time.sleep(sleepMin * 60)

def requestReadyItems() -> None:
    global gModifiedItemsData
    global gModifiedLookup
    gModifiedItemsData = file_handler.loadJson(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS)
    gModifiedLookup = {item["Perm ID"]: item for item in gModifiedItemsData["DATA"]}
        
    logger.sendMessage("Fetching items from server")
    token = user_auth.getKeyringToken()
    try:
        res = requests.post(definitions.URL_MARKET_ENGINE_FETCH_ITEMS, json={"token": token})
    except Exception as _:
        logger.sendMessage("Could not create post request! Try logging in")
        return
    readyItemsData = res.json()
    if res.status_code != 200:
        logger.sendMessage(f"Something went wrong! Status code: {res.status_code}")
    else:
        logger.sendMessage("Writing items to files")
        file_handler.replaceJsonDataAtomic(definitions.PATH_DATA_CLIENT_READY_ITEMS, readyItemsData)
        newModifiedItemsData = file_handler.loadJson(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS)
        for item in readyItemsData["DATA"]:
            manageModifiedItemsEntry(item, newModifiedItemsData) 
        file_handler.replaceJsonDataAtomic(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS, newModifiedItemsData)

def manageModifiedItemsEntry(scannedItem: dict[str, Any], newModifiedItemsData: dict[str, Any]) -> None:
    # Item already added, skip
    global gModifiedLookup
    if scannedItem["Perm ID"] in gModifiedLookup:
        return
    newData = {
        "Perm ID": scannedItem["Perm ID"],
        "Modified Price": 0.0,
        "Use Modified State": False
    }
    newModifiedItemsData["DATA"].append(newData)