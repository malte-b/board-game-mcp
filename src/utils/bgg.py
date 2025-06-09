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
            - 'url' (str): URL to the similar game's page on BoardGameGeek.
    """
    response = requests.get(f"{BGG_BASE_URL}/hot?type=boardgame")
    root = ET.fromstring(response.content)

    results = []
    for item in root.findall("item"):
        game_id = item.get("id")
        rank = item.get("rank")
        title = item.find("name").get("value")
        year = item.find("yearpublished").get("value") if item.find("yearpublished") is not None else "Unknown"
        url = f"https://boardgamegeek.com/boardgame/{game_id}"
        results.append({"id": game_id, "title": title, "rank": rank, "year": year, "url": url})

    return results

def get_similar_games(game_id, limit=5):
    """
    Get a list of games similar to the specified game from the recommend games API.

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
        # Filter out all games with less than 30 votes (num_votes)
        results = [game for game in results if game.get('num_votes', 0) >= 30]
        # Filter out all games with a rec_rating of 0
        results = [game for game in results if game.get('rec_rating', 0) > 0]
        # Sort results by rec_rating, bayes_rating and avg_rating
        results.sort(key=lambda x: (x.get('rec_rating', 0), x.get('bayes_rating', 0), x.get('avg_rating', 0)), reverse=True)

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

def get_similar_games_v2(game_id, limit=5, start=0, end=25, noblock=False):
    """
    Retrieves a list of games similar to a specified board game from the RecommendGames API.

    Args:
        game_id (str): The unique BGG ID of the game to find similar games for.
        limit (int): The number of similar games to retrieve.
        start (int, optional): The starting index for the desired range of results. Defaults to 0.
        end (int, optional): The ending index for the desired range of results. Defaults to 25.
        noblock (bool, optional): If True, the request will not timeout. Defaults to False, which sets a 10-second timeout.

    Returns:
        List[dict]: A list of dictionaries, each representing a similar game with the following fields:
            - 'id' (str): The unique BGG ID of the similar game.
            - 'title' (str): The official title of the similar game.
            - 'year' (str): The year the similar game was published (or 'Unknown' if not available).
            - 'description' (str): A brief description of the similar game.
            - 'url' (str): URL to the similar game's page on BoardGameGeek.
        Returns an empty list if there are any errors during the API request or data processing.
    """

    api_url = f"https://recommend.games/api/games/{game_id}/similar.json"
    params = {
        'num_votes__gte': 30,
        'ordering': '-rec_rating,-bayes_rating,-avg_rating'
    }

    all_games = []

    try:
        for i in range(start+1, end+1):
            params['page'] = i
            response = requests.get(api_url, params=params, timeout=None if noblock else 10)
            response.raise_for_status()
            api_data = response.json()

            games = api_data.get('results', [])
            if not games:
                break

            processed_games = [
                {
                    'id': str(game.get('bgg_id', '')),
                    'title': str(game.get('name', '')),
                    'year': str(game.get('year', 'Unknown')),
                    'description': str(game.get('description', 'No description available')),
                    'url': str(game.get('url', '')),
                }
                for game in games
                if game.get('num_votes', 0) >= 30 and game.get('rec_rating', 0) > 0.001
            ]

            all_games.extend(processed_games)

            # Check if we have enough results
            if len(all_games) >= end or not api_data.get('next'):
                break

        return all_games[:limit] if limit > 0 else all_games

    except requests.RequestException as e:
        print(f"Error fetching similar games: {e}")
        return []
    except ValueError as e:
        print(f"Error: {e}")
        return []
