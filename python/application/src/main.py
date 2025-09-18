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
from main_window import MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import qt_resource
import auth_server
import os
import item_memory
import fwatcher_manager
import validator
import tradeup_memory
import asyncio
from qasync import QEventLoop
import path
import definitions
import logger
import tempfile
import filelock
sys.path.insert(0, path.PATH_SHARE)

g_instanceLockFile = None

def main():
	init()

def init():
    setEnvironment()
    checkInstanceRunning()
    validator.validateFiles()
    auth_server.init()
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    asyncioLoop = QEventLoop(app)
    asyncio.set_event_loop(asyncioLoop)
    qt_resource.loadAppResources()
    window = MainWindow() 
    window.show()
    item_memory.init()
    tradeup_memory.init()
    fwatcher_manager.init()

    app.aboutToQuit.connect(asyncioLoop.stop)
    with asyncioLoop:
        asyncioLoop.run_forever()

def setEnvironment():
    libPath = str(definitions.PATH_LIB)
    if definitions.SYSTEM == definitions.SYSTEM_WINDOWS:
        os.environ["PATH"] = libPath + os.pathsep + os.environ.get("PATH", "")
    elif definitions.SYSTEM == definitions.SYSTEM_LINUX:
        os.environ["LD_LIBRARY_PATH"] = libPath + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
    logger.sendMessage(f"Using Library Path [ {libPath} ]")

def checkInstanceRunning():
    global g_instanceLockFile
    lockPath = os.path.join(tempfile.gettempdir(), 'market_engine_client.lock')
    g_instanceLockFile = open(lockPath, 'w')

    try:
        if definitions.SYSTEM == definitions.SYSTEM_WINDOWS:
            import msvcrt
            msvcrt.locking(g_instanceLockFile.fileno(), msvcrt.LK_NBLCK, 1)
        elif definitions.SYSTEM == definitions.SYSTEM_LINUX:
            import fcntl
            fcntl.flock(g_instanceLockFile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, IOError):
        print("Another instance is already running.")
        sys.exit(1)

if __name__ == "__main__":
	main()