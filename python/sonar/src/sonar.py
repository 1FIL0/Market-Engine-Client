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
import requests
import time
import definitions
import keyring
import logger
import file_handler

sleepMin = 5
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
    gModifiedItemsData = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS))
    gModifiedLookup = {item["Perm ID"]: item for item in gModifiedItemsData["DATA"]}
        
    logger.sendMessage("Fetching items from server")
    
    accessToken = keyring.get_password("market_engine_client", "access_token")
    if not accessToken:
        logger.sendMessage("No access token found")
        return

    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Accept": "application/json"
    }

    try:
        res = requests.post(definitions.URL_MARKET_ENGINE_FETCH_ITEMS, headers=headers, timeout=5)
    except Exception as _:
        logger.sendMessage("Could not fetch items. Check server status")
        return
    if res.status_code != 200:
        logger.sendMessage(f"Something went wrong! Status code: {res.status_code}, Error: {res.text}")
        return
        
    logger.sendMessage(f"Status code: {res.status_code}")
    saveReadyItems(res.json())

def saveReadyItems(readyItemsData: dict[str, Any]):
    logger.sendMessage("Writing items to files")
    file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_CLIENT_READY_ITEMS), readyItemsData)
    newModifiedItemsData = file_handler.loadJson(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS))
    for item in readyItemsData["DATA"]:
        manageModifiedItemsEntry(item, newModifiedItemsData) 
    file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_CLIENT_MODIFIED_ITEMS), newModifiedItemsData)

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