import sys
from datetime import date
from json import dump
from os import makedirs, walk
from os.path import exists, join, splitext
from typing import Any

import requests
import xmltodict
import yaml

API2_BASE_URL = "https://boardgamegeek.com/xmlapi2"

IN_PATH = "./in"
OUT_PATH = "./out"

# bgg item types
BOARDGAME_TYPE = "boardgame"
EXPANSION_TYPE = "boardgameexpansion"


class Result:
    def __init__(self):
        self.boardgames = []
        self.expansions = []


def get_sources() -> list[str]:
    # create in_path dir and exit if it does not exist
    if not exists(IN_PATH):
        makedirs(IN_PATH)
        sys.exit(f"Created src directory {IN_PATH}. Add '.yaml' files to it and rerun")

    # retrieve data source files from in_path
    sources = next(walk(IN_PATH))[2]
    for src in sources:
        ext = splitext(src)[1]
        if ext != ".yaml" and ext != ".yml":
            print(f"Error: could not process '{src}' because it is not a .yaml file")
            sources.remove(src)

    # quit if no valid source files are found
    if not sources:
        sys.exit("Error: no valid source files exist in the 'in' directory")
    return sources


def read_source(src: str) -> "list[int]":
    with open(join(IN_PATH, src), "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        if data and "bgg-ids" in data:
            ids = data["bgg-ids"]
            if not ids:
                return None

            # remove non int values from list
            for id in ids:
                if not isinstance(id, int):
                    ids.remove(id)
            return ids
        else:
            return None


def write_results(src: str, results: Result) -> None:
    today = date.today()
    path = f"{OUT_PATH}/{src}/{today.strftime('%Y-%m')}"
    filename = f"{today}.json"

    # create out dirs if they do not exist
    if not exists(path):
        makedirs(path)

    with open(join(path, filename), "w") as f:
        dump(results.__dict__, f, indent=4, ensure_ascii=False)

    print(f"{src} results successfully written to {path}/{filename}")


def get_items(ids: "list[int]") -> dict:
    ids_str = ",".join(map(str, ids))
    url = f"{API2_BASE_URL}/thing?id={ids_str}&type={BOARDGAME_TYPE},{EXPANSION_TYPE}&stats=1"
    response = requests.get(url)
    if response.status_code == 200:
        resp_dict = xmltodict.parse(response.content)
        return resp_dict
    else:
        # TODO: provide better error handling and logging for bad requests
        sys.exit(f"Error: HTTP {response.status_code}: {response.content}")


def parse_item_name(name_dict: dict) -> str:
    if isinstance(name_dict, list):
        return name_dict[0]["@value"]
    else:
        return name_dict["@value"]


def parse_item_rank(ranks_dict: dict) -> Any:
    if isinstance(ranks_dict, dict):
        rank_dict = ranks_dict["rank"]
        if isinstance(rank_dict, list):
            return rank_dict[0]["@value"]
        else:
            return rank_dict["@value"]
    else:
        return "Not Ranked"


def parse_item_float_val(key_dict: dict) -> Any:
    value = key_dict["@value"]
    if value != "":
        return float(value)
    else:
        return 0.0


def parse_item(item_dict: dict, results: Result) -> None:
    item = {
        "name": parse_item_name(item_dict["name"]),
        "year": item_dict["yearpublished"]["@value"],
        "rating": round(
            parse_item_float_val(item_dict["statistics"]["ratings"]["average"]), 2
        ),
        "rank": parse_item_rank(item_dict["statistics"]["ratings"]["ranks"]),
        "weight": round(
            parse_item_float_val(item_dict["statistics"]["ratings"]["averageweight"]), 2
        ),
        "players": item_dict["minplayers"]["@value"]
        + "-"
        + item_dict["maxplayers"]["@value"],
        "time": item_dict["minplaytime"]["@value"]
        + "-"
        + item_dict["maxplaytime"]["@value"],
        "id": int(item_dict["@id"]),
    }
    type = item_dict["@type"]

    if type == BOARDGAME_TYPE:
        results.boardgames.append(item)
    elif type == EXPANSION_TYPE:
        results.expansions.append(item)


def sortby_rank(x: dict) -> Any:
    try:
        return int(x["rank"])
    except ValueError:
        return float("inf")


if __name__ == "__main__":
    # process each data source file
    sources = get_sources()
    for src in sources:
        # read board game ids from src file
        board_game_ids = read_source(src)
        if not board_game_ids:
            print(
                f"\tError: could not process '{src}' because it does not contain non-empty id list 'bgg-ids' at root"
            )
            continue

        # get items from BGG
        resp_dict = get_items(board_game_ids)
        items = resp_dict["items"]["item"]

        # parse results for item ranks based on structure
        results = Result()
        if isinstance(items, list):
            for item in items:
                parse_item(item, results)
        else:
            item = items
            parse_item(item, results)

        # sort boardgames by rank and expansions by rating
        if results.boardgames:
            results.boardgames.sort(key=sortby_rank)
        if results.expansions:
            results.expansions.sort(key=lambda x: x["rating"], reverse=True)

        # write results to json file
        src_name = splitext(src)[0]
        write_results(src_name, results)
