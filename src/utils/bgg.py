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

def get_game_details(game_ids):
    """
    Get detailed information for one or more board games.
    
    Args:
        game_ids (str or list): Single game ID or comma-separated list of IDs
        
    Returns:
        List[dict]: Detailed game information including mechanics, categories, ratings, etc.
    """
    if isinstance(game_ids, list):
        game_ids = ",".join(game_ids)
    
    response = requests.get(f"{BGG_BASE_URL}/thing?id={game_ids}&stats=1")
    root = ET.fromstring(response.content)
    
    games = []
    for item in root.findall("item"):
        game = {
            "id": item.get("id"),
            "title": item.find("name[@type='primary']").get("value"),
            "description": item.find("description").text if item.find("description") is not None else "No description available",
            "year": item.find("yearpublished").get("value") if item.find("yearpublished") is not None else "Unknown",
            "min_players": item.find("minplayers").get("value") if item.find("minplayers") is not None else "Unknown",
            "max_players": item.find("maxplayers").get("value") if item.find("maxplayers") is not None else "Unknown",
            "playing_time": item.find("playingtime").get("value") if item.find("playingtime") is not None else "Unknown",
            "complexity": None,
            "rating": None,
            "categories": [],
            "mechanics": []
        }
        
        # Extract ratings and complexity
        ratings = item.find("statistics/ratings")
        if ratings is not None:
            avg_rating = ratings.find("average")
            if avg_rating is not None:
                game["rating"] = avg_rating.get("value")
            
            complexity_elem = ratings.find("averageweight")
            if complexity_elem is not None:
                game["complexity"] = complexity_elem.get("value")
        
        # Extract categories and mechanics
        for link in item.findall("link"):
            link_type = link.get("type")
            if link_type == "boardgamecategory":
                game["categories"].append(link.get("value"))
            elif link_type == "boardgamemechanic":
                game["mechanics"].append(link.get("value"))
        
        games.append(game)
    
    return games

def get_hot_games():
    """
    Get a list of the Top 50 trending games today from BoardGameGeek.

    Returns:
        List[dict]: A list of dictionaries, each representing a popular game with the following fields:
            - 'id' (str): The unique BGG ID of the game.
            - 'title' (str): The official title of the game.
            - 'rank' (str): The current hotness rank of the game on BGG.
            - 'year' (str): The year the game was published (or 'Unknown' if not available).
    """
    response = requests.get(f"{BGG_BASE_URL}/hot?type=boardgame")
    root = ET.fromstring(response.content)

    results = []
    for item in root.findall("item"):
        game_id = item.get("id")
        rank = item.get("rank")
        title = item.find("name").get("value")
        year = item.find("yearpublished").get("value") if item.find("yearpublished") is not None else "Unknown"
        results.append({"id": game_id, "title": title, "rank": rank, "year": year})

    return results

