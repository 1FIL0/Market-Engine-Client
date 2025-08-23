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
### Base
Firstly, clone the mandatory repositories: ```git clone https://github.com/1FIL0/Market-Engine-Client market_engine_client && 
git clone https://github.com/1FIL0/Market-Engine-Share market_engine_share && 
git clone https://github.com/1FIL0/Market-Engine-Assets market_engine_assets &&
git clone https://github.com/1FIL0/Market-Engine-Shell-Network market_engine_shell_network```

The rest happens in the shell network, supports msys2 and linux:    
```cd market_engine_shell_network/configure && ./configure_qt_docs.sh && cd ../make```  

### Make AppImage
Download the appimagetool from https://github.com/AppImage/appimagetool and place it in appimg/
```./mk_appimg_client.sh PLATFORM=LINUX_X86_64 MAKE_BINARIES=TRUE```  
The AppImage will be stored in the appimg/ directory

### Make 7Zip
Windows: ```./mk_zip_client PLATFORM=WINDOWS_X86_64 MAKE_BINARIES=TRUE```  
Linux: ```./mk_zip_client PLATFORM=LINUX_X86_64 MAKE_BINARIES=TRUE```  
The archives will be created in the zip/ directory

## Licence
Market Engine is licenced under the GPL v3.0 licence
