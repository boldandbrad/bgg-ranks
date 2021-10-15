# BGG Ranks

Simple script that grabs Board Game data from BoardGameGeek.com via the [BGG XML API2](https://boardgamegeek.com/wiki/page/BGG_XML_API2)

## Dependencies

- python 3.5+
- python packages listed in [requirements.txt](requirements.txt)

## Usage

1. Create one or more `.yaml` files at `./in/` with the following format:

    ```yaml
    # collection.yaml
    board-games:
    - 266192    # BGG ids
    - 266524
    ```

    > BGG ids can be easily stripped from the board game page urls on [boardgamegeek.com](https://boardgamegeek.com)

2. Update the `data_sources` list in `bgg_ranks.py` to include the created yaml file, without extension:

    ```py
    data_sources = [
        'collection',
    ]
    ```

3. Run the `bgg_ranks.py` script:

    ```zsh
    python bgg_ranks.py
    ```

4. Script will create an out files for each source in `data_sources`, with the following format:

    ```txt
    ./out/collection/collection-yyyy-mm-dd.json
    ```

    Each out file contains a simple json list containing an object for each game id provided in the corresponding source file. The list will always be sorted by `rank` in ascending order.

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
