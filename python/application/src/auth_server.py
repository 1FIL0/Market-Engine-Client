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

import os
import sys
from typing import Any, Callable
import webbrowser
import path
sys.path.insert(0, path.PATH_SHARE)
import base64
import hashlib
from flask import Flask, request
import threading
import urllib.parse
import requests
import keyring
import logger
from auth_user_data import AuthUserData

gServer = None
gAuthorizedCallback = None
gCodeVerifier = None
gAccessToken = None
gIDToken = None
gAuthUserData = None

URL_CLIENT_AUTH_CALLBACK = "http://localhost:5000/auth_callback"
URL_AUTH0_DOMAIN = "https://marketengine.eu.auth0.com"
CLIENT_ID = "n5CZq2xT91SO1Idfv2klRnyxflhQgTCW"

def init():
    refreshTokens()
    runServer()

def runServer():
    createServer()
    threading.Thread(
        target=lambda: gServer.run(
            host="127.0.0.1", port=5000, debug=False, use_reloader=False
        ),
        daemon=True
    ).start()

def createServer():
    global gServer
    gServer = Flask(__name__)

    @gServer.route("/auth_callback")
    def authCallback():  # pyright: ignore[reportUnusedFunction]
        authCode = request.args.get("code")

        payload = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code_verifier": gCodeVerifier,
            "code": authCode,
            "redirect_uri": URL_CLIENT_AUTH_CALLBACK
        }
        res = fetchTokens(payload=payload)
        if res.status_code != 200:
            return "Error, something went wrong"
        return "Success, you may close this page"

    return gServer

def fetchTokens(payload: dict[str, Any]):
    global gAccessToken, gIDToken
    headers = { "content-type": "application/x-www-form-urlencoded" }
    res = requests.post(f"{URL_AUTH0_DOMAIN}/oauth/token", data=payload, headers=headers)
    if res.status_code != 200:
        logger.sendMessage(f"Unable to fetch tokens {res.text}")
        return
    logger.sendMessage(f"Fetched tokens")
    tokensData = res.json()
    gAccessToken = tokensData.get("access_token")
    gIDToken = tokensData.get("id_token")
    refreshToken = tokensData.get("refresh_token")
    if refreshToken:
        keyring.set_password("market_engine_client", "refresh_token", refreshToken)
    keyring.set_password("market_engine_client", "access_token", gAccessToken)
    keyring.set_password("market_engine_client", "id_token", gIDToken)
    constructAuthUserData()

    if gAuthorizedCallback:
        gAuthorizedCallback()

    return res

def refreshTokens():
    refreshToken = keyring.get_password("market_engine_client", "refresh_token")
    
    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "refresh_token": refreshToken
    }
    fetchTokens(payload=payload)

def constructAuthUserData():
    global gAuthUserData
    gAuthUserData = AuthUserData()

    headers = {
        "Authorization": f"Bearer {gAccessToken}",
        "Accept": "application/json"
    }
    res = requests.get(f"{URL_AUTH0_DOMAIN}/userinfo", headers=headers)

    if res.status_code != 200:
        logger.sendMessage(f"Failed to retrieve user info: {res.text}")
        return

    data = res.json()
    gAuthUserData.name = data.get("name")
    gAuthUserData.picture = data.get("picture")
    logger.sendMessage(f"Retrieved user info")

def base64urlEncode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def getAuthorizationURL() -> str:
    global gCodeVerifier
    gCodeVerifier = base64urlEncode(os.urandom(32))
    codeChallenge = base64urlEncode(hashlib.sha256(gCodeVerifier.encode("utf-8")).digest())
    state = base64urlEncode(os.urandom(32))

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": URL_CLIENT_AUTH_CALLBACK,
        "scope": "openid profile offline_access",
        "state": state,
        "code_challenge": codeChallenge,
        "code_challenge_method": "S256"
    }
    url = f"{URL_AUTH0_DOMAIN}/authorize?{urllib.parse.urlencode(params)}"

    return url

def openAuthorizationURL() -> None:
    webbrowser.open(getAuthorizationURL())

def setUserAuthorizedCallback(callback: Callable[[], None]):
    global gAuthorizedCallback
    gAuthorizedCallback = callback

def getAuthUserData():
    return gAuthUserData

def getAccessToken():
    return gAccessToken
