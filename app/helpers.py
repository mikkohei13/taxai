import sys
import requests
import json

import my_token

def fetch_finbif_api(api_url):
    if "access_token=" not in api_url:
        print("WARNING: access_token param is missing from your url!")

    api_url = api_url + my_token.LAJIFI_TOKEN
    print("Fetching API: ", api_url)

    try:
        r = requests.get(api_url)
    except ConnectionError:
        print("ERROR: api.laji.fi complete error.")

    data_json = r.text
    data_dict = json.loads(data_json)

    if "status" in data_dict:
        if 403 == data_dict["status"]:
            print("ERROR: api.laji.fi 403 error.")
            raise ConnectionError

    return data_dict

