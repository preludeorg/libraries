import flask.cli
import logging
import requests
import threading
import time
import webbrowser
from flask import Flask, request


OIDC_CLIENT_ID = "XXX"
OIDC_FLASK_REDIRECT_URI = "http://localhost:5173"
OIDC_REDIRECT_URI = "https://platform.us2.preludesecurity.com"
OIDC_AUTHORIZATION_URL = (
    "https://platform-auth.us2.preludesecurity.com/oauth2/authorize"
)
OIDC_TOKEN_URL = "https://platform-auth.us2.preludesecurity.com/oauth2/token"
OIDC_SCOPE = "openid+profile+email"
OIDC_IDP = "Google"


app = Flask(__name__)
app.logger.disabled = True
logging.getLogger('werkzeug').disabled = True
flask.cli.show_server_banner = lambda *args: None
tokens = None


def get_auth_url(redirect_uri: str) -> str:
    return f"{OIDC_AUTHORIZATION_URL}?response_type=code&client_id={OIDC_CLIENT_ID}&redirect_uri={redirect_uri}&scope={OIDC_SCOPE}&identity_provider={OIDC_IDP}"


def exchange_for_tokens(code: str, redirect_uri: str) -> dict:
    resp = requests.post(
        OIDC_TOKEN_URL,
        data={
            "client_id": OIDC_CLIENT_ID,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
    )
    if resp.status_code != 200:
        print("Error exchanging code for tokens:", resp.text, resp.status_code)
    resp = resp.json()
    return dict(
        expires=resp.get("expires_in"),
        token=resp.get("id_token"),
        refresh_token=resp.get("refresh_token"),
    )


def run_flask():
    app.run(port=5173, debug=False, use_reloader=False)


@app.route("/")
def callback():
    if code := request.args.get("code"):
        global tokens
        tokens = exchange_for_tokens(code, OIDC_FLASK_REDIRECT_URI)
        return "Authentication successful! You can close this window now."
    return "Error: No code received."


def authorize_with_flask():
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()
    auth_url = get_auth_url(OIDC_FLASK_REDIRECT_URI)
    webbrowser.open(auth_url)
    while tokens is None:
        time.sleep(1)
    return tokens
