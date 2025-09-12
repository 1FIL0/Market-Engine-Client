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
from qasync import QEventLoop  # pyright: ignore[reportMissingTypeStubs]
import path
import definitions
import logger
sys.path.insert(0, path.PATH_SHARE)

def main():
	init()

def init():
    setEnvironment()
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

if __name__ == "__main__":
	main()