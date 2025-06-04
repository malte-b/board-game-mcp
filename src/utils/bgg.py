import requests
from xml.etree import ElementTree as ET

BGG_BASE_URL = 'https://boardgamegeek.com/xmlapi2'

def search(query):
    """
    Search for board games on BoardGameGeek by title.

    Args:
        query (str): The name (or partial name) of the board game to search for.

    Returns:
        List[dict]: A list of dictionaries, each representing a matching game with the following fields:
            - 'id' (str): The unique BGG ID of the game.
            - 'title' (str): The official title of the game.
            - 'year' (str): The year the game was published (or 'Unknown' if not available).

    Example:
        >>> search_game("Catan")
        [
            {"id": "13", "title": "Catan", "year": "1995"},
            ...
        ]
    """

    response = requests.get(f"{BGG_BASE_URL}/search?query={query}")
    root = ET.fromstring(response.content)

    results = []
    for item in root.findall("item"):
        game_id = item.get("id")
        title = item.find("name").get("value")
        year = item.find("yearpublished").get("value") if item.find("yearpublished") is not None else "Unknown"
        results.append({"id": game_id, "title": title, "year": year})

    return results

