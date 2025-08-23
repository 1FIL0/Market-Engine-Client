![](readme_assets/market_engine_client.png)
# Market Engine Client

## Overview
A powerful GPU-Powered CS2 Tradeup engine designed to brute-force profitable tradeups. Configure max input floats for an easier time finding items on the market, Select your CPU or your GPU's as you like, 
and manage tradeups easily via the tradeups tab. Includes an item viewer page for every skin and shows it's details, a manager for changing skin prices if they're off, and more.

## Downloads
Downloads are listed on the Market Engine website (https://website.com) and github releases. Currently the project supports Windows and Linux

## How to use
In order to use the client, you must either setup your own API from https://github.com/1FIL0/Market-Engine-API or login through the accounts page
in the client to use the official API over at https://website.com. To start finding tradeups simply go to the sonar tab and automatically scan for new items
intervally. Then head over to the tradeup engine tab and run the engine. Make sure to configure all of your hardware in the settings.

## Building from source
## README IN PROGRESS
<!--
### First steps
Firstly, clone the mandatory repositories:  ```mkdir MarketEngine && cd MarketEngine &&
git clone https://github.com/1FIL0/Market-Engine-Client market_engine_client && 
git clone https://github.com/1FIL0/Market-Engine-Share market_engine_share && 
git clone https://github.com/1FIL0/Market-Engine-Assets market_engine_assets &&
git clone https://github.com/1FIL0/Market-Engine-Shell-Network market_engine_shell_network```

### Windows Build Setup
install python from https://www.python.org/ then open powershell and navigate to the MarketEngine root directory.  
create virtual environment and install packages:  
```New-Item -ItemType Directory -Path venvs/windows_x86_64/client_venv -Force;source venvs/windows_x86_64/client_venv/Scripts/activate; py -m pip install pyqt5 pyopencl requests pyinstaller keyring```  
install msys2 from https://www.msys2.org/ and open its mingw64 terminal to install packages (Launch again if it closes after update):  
```pacman -Syu && pacman -S  mingw-w64-x86_64-toolchain mingw-w64-x86_64-openssl mingw-w64-x86_64-opencl-icd mingw-w64-x86_64-opencl-clhpp mingw-w64-x86_64-opencl-headers  mingw-w64-x86_64-rapidjson```

### Linux Build Setup
create virtual environment and install packages:  
```mkdir -p venvs/linux_x86_64/client_venv && source venvs/linux_x86_64/client_venv/bin/activate && python3 -m pip install pyqt5 pyopencl requests pyinstaller keyring && sudo apt update -y && sudo apt install opencl-headers opencl-cl-hpp-headers rapidjson-dev libssl-dev```

### Make 7Zip
you must use the msys2 mingw64 terminal if you're using windows  
Windows: ```cd market_engine_shell_network/configure && ./configure_qt_docs.sh && cd ../make && /mk_zip_client PLATFORM=WINDOWS_X86_64 MAKE_BINARIES=TRUE```  
Linux: ```cd market_engine_shell_network/configure && ./configure_qt_docs.sh && cd ../make && ./mk_zip_client PLATFORM=LINUX_X86_64 MAKE_BINARIES=TRUE```  
The archives will be created in the zip/ directory

### Make AppImage
Download the appimagetool from https://github.com/AppImage/appimagetool and place it in appimg/  
```cd market_engine_shell_network/configure && ./configure_qt_docs.sh && cd ../make && ./mk_appimg_client.sh PLATFORM=LINUX_X86_64 MAKE_BINARIES=TRUE```  
The AppImage will be stored in the appimg/ directory
-->

## Licence
Market Engine is licenced under the GPL v3.0 licence





