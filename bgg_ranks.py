from datetime import date
import json
from os import makedirs, walk
from os.path import exists, join, splitext
import sys
from typing import Any

import requests
import xmltodict
import yaml

api2_base_url = "https://boardgamegeek.com/xmlapi2"

in_path = "./in"
out_path = "./out"


def get_sources() -> list[str]:
    # create in_path dir and exit if it does not exist
    if not exists(in_path):
        makedirs(in_path)
        sys.exit(f"Created src directory {in_path}. Add '.yaml' files to it and rerun")

    # retrieve data source files from in_path
    sources = next(walk(in_path))[2]
    for src in sources:
        ext = splitext(src)[1]
        if ext != ".yaml":
            print(f"Error: could not process '{src}' because it is not a .yaml file")
            sources.remove(src)

    if not sources:
        sys.exit(f"Error: no valid source files exist in the 'in' directory")
    return sources


def read_source(src: str) -> "list[int]":
    with open(join(in_path, src), "r") as f:
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


def write_results(src: str, results: dict) -> None:
    path = f"{out_path}/{src}"
    filename = f"{date.today()}.json"

    # create out dirs if they do not exist
    if not exists(path):
        makedirs(path)

    with open(join(path, filename), "w") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"{src} results successfully written to {path}/{filename}")


def get_items(ids: "list[int]") -> dict:
    ids_str = ",".join(map(str, ids))
    url = (
        f"{api2_base_url}/thing?id={ids_str}&type=boardgame,boardgameexpansion&stats=1"
    )
    response = requests.get(url)
    if response.status_code == 200:
        resp_dict = xmltodict.parse(response.content)
        return resp_dict
    else:
        # TODO: provide better error handling and logging for bad requests
        sys.exit(f"Error: HTTP {response.status_code}: {response.content}")


def parse_item_name(item_dict: dict) -> str:
    name_dict = item_dict["name"]
    if isinstance(name_dict, list):
        return name_dict[0]["@value"]
    else:
        return name_dict["@value"]


def parse_item_type(item_dict: dict) -> str:
    type = item_dict["@type"]
    if type == "boardgameexpansion":
        type = "expansion"
    return type


def parse_item_rank(item_dict: dict) -> Any:
    rank_dict = item_dict["statistics"]["ratings"]["ranks"]["rank"]
    if isinstance(rank_dict, list):
        return rank_dict[0]["@value"]
    else:
        return rank_dict["@value"]


def parse_item(item_dict: dict, results: dict) -> None:
    item = {
        "name": parse_item_name(item_dict),
        "year": item_dict["yearpublished"]["@value"],
        "rating": round(
            float(item_dict["statistics"]["ratings"]["average"]["@value"]), 2
        ),
        "rank": parse_item_rank(item_dict),
        "weight": round(
            float(item_dict["statistics"]["ratings"]["averageweight"]["@value"]), 2
        ),
        "players": item_dict["minplayers"]["@value"]
        + "-"
        + item_dict["maxplayers"]["@value"],
        "time": item_dict["minplaytime"]["@value"]
        + "-"
        + item_dict["maxplaytime"]["@value"],
        "id": int(item_dict["@id"]),
    }
    type = parse_item_type(item_dict)

    if type == "boardgame":
        results["boardgames"].append(item)
    elif type == "expansion":
        results["expansions"].append(item)


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
        results = {
            "boardgames": [],
            "expansions": [],
        }
        if isinstance(items, list):
            for item in items:
                parse_item(item, results)
        else:
            item = items
            parse_item(item, results)

        # sort boardgames by rank and expansions by rating
        if results["boardgames"]:
            results["boardgames"].sort(key=lambda x: int(x["rank"]))

        if results["expansions"]:
            results["expansions"].sort(key=lambda x: x["rating"], reverse=True)

        # write results dict to json file
        src_name = splitext(src)[0]
        write_results(src_name, results)
