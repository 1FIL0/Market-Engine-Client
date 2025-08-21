import sys
import path
sys.path.insert(0, path.PATH_SHARE)
from flask import Flask, request
import threading
import user_auth

gApp = None

def createApp():
    global gApp
    if gApp is None:
        app = Flask(__name__)

        @app.route('/')
        def home():  # pyright: ignore[reportUnusedFunction]
            return "Market Engine server daemon is running."

        @app.route('/callback')
        def authTokenCallback():  # pyright: ignore[reportUnusedFunction]
            token = request.args.get('token')
            if not token: return "No token received.", 500
            print("Token Received")
            user_auth.processServerToken(token)
            return "Login successful! You can close this window.", 200

        gApp = app
    return gApp

def runServer():
    createApp()
    threading.Thread(
        target=lambda: gApp.run(
            host='127.0.0.1', port=5000, debug=False, use_reloader=False
        ),
        daemon=True
    ).start()

