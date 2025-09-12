import sys
import path
sys.path.insert(0, path.PATH_SHARE)
import proc
import definitions
import shared_args

gProcApp = None

def main():
    launchApp()

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
    