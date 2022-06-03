import requests


def get_user(access_token):
    return requests.get(f"https://graph.facebook.com/v2.3/me?access_token={access_token}&fields=name%2Cemail&locale=en_US&method=get&pretty=0&sdk=joey&suppress_http_code=1").json()
