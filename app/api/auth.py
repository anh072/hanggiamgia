from collections import defaultdict
import time

import requests
from flask import current_app
import jwt


cache = defaultdict(str)


def _get_access_token():
    res = requests.post(
      f"https://{current_app.config['AUTH0_API_DOMAIN']}/oauth/token",
      data={
        'grant_type': "client_credentials",
        'client_id': current_app.config["AUTH0_API_CLIENT_ID"],
        'client_secret': current_app.config["AUTH0_API_CLIENT_SECRET"],
        'audience': current_app.config["AUTH0_API_AUDIENCE"]
      }
    )
    res.raise_for_status()
    access_token = res.json().get("access_token")
    return access_token


def get_access_token():
    access_token = cache.get("access_token")
    if access_token:
        claims = jwt.decode(access_token, options={"verify_signature": False})
        current_time = time.time()
        if current_time > claims["exp"]:
            current_app.logger.info("Access token has expired")
            current_app.logger.info("Getting a new access token")
            access_token = _get_access_token()
    else:
        current_app.logger.info("Access token is not in cache. Getting a new one")
        access_token = _get_access_token()
    cache["access_token"] = access_token
    return access_token