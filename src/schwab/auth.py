import os
import base64
import requests
import webbrowser
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs/app.log", format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


def get_access_token():
    """
    Use the refresh token stored in GitHub Secrets to retrieve a new access token which is then returned.

    TODO: Confirm return value. 
    """
    logger.debug("Entered the get_access_token function.")
    app_key = os.environ["Schwab_app_key"]
    app_secret = os.environ["Schwab_app_secret"]
    refresh_token = os.environ["Schwab_refresh_token"]
    headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{app_key}:{app_secret}", "utf-8")).decode("utf-8")}',
               'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    resp = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
    resp.raise_for_status()

    access_token = resp["access_token"]
    logger.debug("About to return from the get_access_token function.")
    return access_token


def get_refresh_token(callback_url: str="https://127.0.0.1"):
    """"
    This is a function that must be executed manually once weekly.  The resulting refresh token must then be placed into secure storage to get a new bearer token.
    Input:
    ------
    callback_url: the URL to call back to post-authorization.
    """
    app_key = os.environ['Schwab_app_key']
    app_secret = os.environ['Schwab_app_secret']

    auth_url = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri={callback_url}'
    webbrowser.open(url=auth_url, new=1)

    response_url = input("Enter the URL provided by the authorization here:  ")
    authorization_code = f"{response_url[response_url.index('code=') + 5:response_url.index('%40')]}@"

    headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{app_key}:{app_secret}", "utf-8")).decode("utf-8")}', 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'authorization_code', 'code': authorization_code, 'redirect_uri': callback_url}
    try:
        resp = requests.post(auth_url, headers=headers, data=data)
        if resp.ok():
            refresh_token = resp.get("refresh_token")
    except:
        raise Exception("Authorization request failed.")

    return refresh_token


if __name__=="__main__":
    print(get_refresh_token())