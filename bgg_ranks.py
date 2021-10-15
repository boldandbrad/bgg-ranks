
from datetime import date
import json
import os
import sys

import requests
import xmltodict
import yaml

api2_base_url = 'https://boardgamegeek.com/xmlapi2'

in_path = './in'
out_path = './out'

# TODO: call on every file in in_path instead of hardcoded values
data_sources = [
    'cabinet',
    'watchlist'
]

def read_source(src: str) -> 'list[int]':
    filename = f'{src}.yaml'

    # create in dir if it does not exist
    if not os.path.exists(in_path):
        os.makedirs(in_path)
        sys.exit(f'Error: no source files exist in the \'in\' directory')

    with open(os.path.join(in_path, filename), 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        if 'board-games' in data:
            return data['board-games']
        else:
            sys.exit(f'Error: {filename} does not contain id list \'board-games\'')

def write_results(src: str, results: dict) -> None:
    today = date.today()
    path = f'{out_path}/{src}'
    filename = f'{src}-{today}.json'

    # create out dirs if they do not exist
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, filename), 'w') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f'{src} results successfully written to {path}/{filename}')

def get_items(ids: 'list[int]') -> dict:
    ids_str = ','.join(map(str, ids))
    url = f'{api2_base_url}/thing?id={ids_str}&type=boardgame&stats=1'
    response = requests.get(url)
    if response.status_code == 200:
        resp_dict = xmltodict.parse(response.content)
        return resp_dict
    else:
        sys.exit(f'Error: HTTP {response.status_code}: {response.content}')

def get_item_name(item_dict: dict) -> str:
    name_dict = item_dict['name']
    if isinstance(name_dict, list):
        return name_dict[0]['@value']
    else:
        return name_dict['@value']

def get_item_rank(item_dict: dict) -> int:
    rank_dict = item_dict['statistics']['ratings']['ranks']['rank']
    if isinstance(rank_dict, list):
        return int(rank_dict[0]['@value'])
    else:
        return int(rank_dict['@value'])

def parse_item(item_dict) -> dict:
    name = get_item_name(item_dict)
    rank = get_item_rank(item_dict)
    weight = round(float(item_dict['statistics']['ratings']['averageweight']['@value']), 2)
    id = int(item_dict['@id'])
    return {'name': name, 'rank': rank, 'weight': weight, 'id': id}


if __name__ == '__main__':
    for src in data_sources:
        # read board game ids from src file
        board_game_ids = read_source(src)

        # get items from BGG
        resp_dict = get_items(board_game_ids)
        items = resp_dict['items']['item']

        # parse results for item ranks
        results = []
        if isinstance(items, list):
            for item in items:
                results.append(parse_item(item))
        else:
            item = items
            results.append(parse_item(item))

        # sort results by rank
        results.sort(key=lambda x: x['rank'])

        # write results dict to json file
        write_results(src, results)
