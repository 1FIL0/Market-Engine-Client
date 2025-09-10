import os
import sys
import path
sys.path.insert(0, path.PATH_SHARE)
import proc
import definitions
import shared_args
import logger

gProcApp = None

def main():
    setEnvironment()
    launchApp()

def setEnvironment():
    libPath = str(definitions.PATH_LIB)
    if definitions.SYSTEM == definitions.SYSTEM_WINDOWS:
        os.environ["PATH"] = libPath + os.pathsep + os.environ.get("PATH", "")
    elif definitions.SYSTEM == definitions.SYSTEM_LINUX:
        os.environ["LD_LIBRARY_PATH"] = libPath + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
    logger.sendMessage(f"Using Library Path [ {libPath} ]")

def launchApp():
    global gProcApp
    cmdList: list[str] = []
    if shared_args.argDist == "dev":
        cmdList = ["python3", "-u", f"{definitions.PATH_DIST_CLIENT_APP_BINARY}", "--dist", "dev"] + sys.argv[1:]
    elif shared_args.argDist == "release" or not shared_args.argDist:
        cmdList = [f"{definitions.PATH_DIST_CLIENT_APP_BINARY}", "--dist", "release"] + sys.argv[1:]
    gProcApp = proc.runSubProcess(cmdList, None, None)
    gProcApp.wait()

if __name__ == "__main__":
	main()
    