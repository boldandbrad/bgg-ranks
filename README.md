# BGG Ranks

Simple script that grabs Board Game data from BoardGameGeek.com via the [BGG XML API2](https://boardgamegeek.com/wiki/page/BGG_XML_API2)

## Dependencies

- python 3.5+
- python packages listed in [requirements.txt](requirements.txt)

## Usage

1. Create one or more `.yaml` source files inside `./in/` with the following format:

    ```yaml
    # collection.yaml
    bgg-ids:
    - 266192    # BGG id ints
    - 266524
    - 290448

    ```

    > BGG ids can be easily stripped from the board game or board game expansion page urls on [boardgamegeek.com](https://boardgamegeek.com)

2. Run the `bgg_ranks.py` script:

    ```zsh
    python bgg_ranks.py
    ```

3. The script will create an output file for each source `.yaml` file in `./in/`, with the following path and name:

    ```txt
    ./out/collection/yyyy-mm-dd.json
    ```

    Each out file contains lists of board game and expansion objects corresponding to the ids provided in the source file. The boardgames list will always be sorted by BGG `rank` in ascending order, while the expansions list will always be sorted by BGG `rating` in descending order.

    ```json
    {
        "boardgames": [
            {
                "name": "Wingspan",
                "year": "2019",
                "rating": 8.11,
                "rank": "21",
                "weight": 2.43,
                "id": 266192
            },
            {
                "name": "PARKS",
                "year": "2019",
                "rating": 7.84,
                "rank": "113",
                "weight": 2.16,
                "id": 266524
            }
        ],
        "expansions": [
            {
                "name": "Wingspan: European Expansion",
                "year": "2019",
                "rating": 8.42,
                "rank": "Not Ranked",
                "weight": 2.38,
                "id": 290448
            }
        ]
    }
    ```

## Coming Soon

- Additional script for aggregating output files into metrics
- Multi-thread requests to api for extremely long id lists?
- Optional csv output for copy/import into spreadsheets

## License

[MIT](LICENSE)
