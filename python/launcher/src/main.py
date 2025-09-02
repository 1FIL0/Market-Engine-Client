import sys
import path
sys.path.insert(0, path.PATH_SHARE)
import proc
import definitions
import shared_args

gProcApp = None

def main():
    global gProcApp
    cmdList: list[str] = []
    if shared_args.argDist == "dev":
        cmdList = ["python3", "-u", f"{definitions.PATH_DIST_CLIENT_APP_BINARY}", "--dist", shared_args.argDist]
    elif shared_args.argDist == "release":
        cmdList = [f"{definitions.PATH_DIST_CLIENT_APP_BINARY}", "--dist", shared_args.argDist]
    gProcApp = proc.runSubProcess(cmdList)
    gProcApp.wait()

if __name__ == "__main__":
    main()