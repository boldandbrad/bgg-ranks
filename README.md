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
    ```

    > BGG ids can be easily stripped from the board game page urls on [boardgamegeek.com](https://boardgamegeek.com)

2. Run the `bgg_ranks.py` script:

    ```zsh
    python bgg_ranks.py
    ```

3. The script will create an output file for each source `.yaml` file in `./in/`, with the following path and name:

    ```txt
    ./out/collection/collection-yyyy-mm-dd.json
    ```

    Each out file contains a simple json list of board game objects corresponding to the ids provided in the source file. The list will always be sorted by BGG `rank` in ascending order.

    ```json
    [
        {
            "name": "Wingspan",
            "rank": 21,
            "weight": 2.43,
            "id": 266192
        },
        {
            "name": "PARKS",
            "rank": 113,
            "weight": 2.16,
            "id": 266524
        }
    ]
    ```

## Coming Soon

- Added support for Board Game Expansions
- Additional script for aggregating output files into metrics

## License

[MIT](LICENSE)
