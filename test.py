import requests
import xmltodict
import yaml

API2_BASE_URL = "https://boardgamegeek.com/xmlapi2"

BOARDGAME_TYPE = "boardgame"


def get_items() -> dict:
    # ids_str = ",".join(map(str, ids))
    url = f"{API2_BASE_URL}/hot?type={BOARDGAME_TYPE}&stats=1"
    response = requests.get(url)
    if response.status_code == 200:
        resp_dict = xmltodict.parse(response.content)
        return resp_dict
    else:
        # TODO: provide better error handling and logging for bad requests
        sys.exit(f"Error: HTTP {response.status_code}: {response.content}")


print(get_items())
