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

    response = requests.get(f"{BGG_BASE_URL}/search?query={query}&exact=0&type=boardgame")
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

def get_similar_games(game_id, limit=5):
    """
    Get a list of games similar to the specified game.

    Args:
        game_id (str): The unique BGG ID of the game to find similar games for.
        limit (int): The number of BGG IDs to retrieve.

    Returns:
        List[dict]: A list of dictionaries, each representing a similar game with the following fields:
            - 'id' (str): The unique BGG ID of the similar game.
            - 'title' (str): The official title of the similar game.
            - 'year' (str): The year the similar game was published (or 'Unknown' if not available).
            - 'description' (str): A brief description of the similar game.
            - 'url' (str): URL to the similar game's page on BoardGameGeek.
    """
    recommended_games = []
    api_url = f"https://recommend.games/api/games/{game_id}/similar.json"
    try: 
        response = requests.get(api_url)
        response.raise_for_status()
        api_data = response.json()
        results = api_data['results']
        for game_data in results[:limit]:
            bgg_id = game_data.get('bgg_id')
            title = game_data.get('name')
            year = game_data.get('year')
            description = game_data.get('description', 'No description available')
            url = game_data.get('url')

            if bgg_id and title:
                formatted_game = {
                    'id': str(bgg_id),
                    'title': str(title),
                    'year': str(year) if year is not None else 'Unknown',
                    'description': str(description),
                    'url': str(url),
                }
                recommended_games.append(formatted_game)

        return recommended_games
    except requests.RequestException as e:
        print(f"Error fetching similar games: {e}")
        return []