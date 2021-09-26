from flask import Flask, request, redirect, session
import requests
import secret
#secret.py contains the client_id and client_secret
import os
import random

app = Flask(__name__)
client_id = secret.client_id
client_secret = secret.client_secret
app.secret_key = secret.client_secret

auth_base = "https://dev-55559903.okta.com/oauth2/default/v1/"
callback_url = "http://localhost:8080/authorization-code/callback"

@app.route("/")
def index():
    """Send index route to /auth code flow """
    return redirect("/auth")

@app.route("/auth")
def login():
    """Initiate authorization code flow, redirect to authentication provider"""
    state = random.randint(1, 100)
    session["state"] = state
    params = {
        "client_id": secret.client_id,
        "redirect_uri": callback_url,
        'scope': "openid profile",
        'state': state,
        'response_type': 'code', 
    }
    auth_uri = f"{auth_base}authorize"
    auth_uri += "?" + requests.compat.urlencode(params)
    return redirect(auth_uri)


@app.route("/authorization-code/callback")
def callback():
    """Receive callback, validate code, redirect to /profile"""
    code = request.args.get("code")
    state = request.args.get("state")
    if int(state) != int(session["state"]):
        return "State Mismatch"
    params = {
        "client_id": secret.client_id,
        "client_secret": secret.client_secret
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "redirect_uri": callback_url,
        "code": code
    }
    token_uri = f"{auth_base}token"
    token_uri += "?" + requests.compat.urlencode(params)
    token = requests.post(token_uri, headers=headers, data=data)
    token_response = token.json()
    session["access_token"] = token_response["access_token"]
    session["id_token"] = token_response["id_token"]
    return redirect("/profile")


@app.route("/profile")
def userinfo():
    """Retreive user details from /userinfo endpoint"""
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + session["access_token"]
    }
    userinfo_uri = f"{auth_base}userinfo"
    userinfo = requests.get(userinfo_uri, headers=headers)
    userinfo_response = userinfo.json()
    session["userinfo"] = userinfo_response
    return "User Info: " + str(userinfo_response)



if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8080
    app.run(host, port, debug=True)