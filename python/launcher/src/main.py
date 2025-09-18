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
    