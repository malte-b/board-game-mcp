import requests

def recommend_similar(id):
    """
    This function recommends the similar games to the BoardGameGeek id provided.
    
    Args:
        id (str): The id of game from BoardGameGeek
        
    Returns:
        List[dict]: A list of dictionaries, each representing a recommended game with the following fields:
            - 'id' (str): The unique BGG ID of the game.
            - 'name' (str): The official title of the game.
            - 'image_url' (str): URL to the game's image.
            - 'year' (int): The year the game was published.
            - 'description' (str): A brief description of the game.
            - 'url' (str): URL to the game's page on BoardGameGeek.
            
    Example:
        >>> recommend_similar("13")
        [
            {
                "id": "12345",
                "name": "Game Title",
                "image_url": "http://example.com/image.jpg",
                "year": 2020,
                "description": "A brief description of the game.",
                "url": "https://boardgamegeek.com/boardgame/12345/game-title"
            },
            ...
        ]
    """

    url = f"https://recommend.games/api/games/{id}/similar.json"

    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)

    json_data = response.json()

    results = []
    
    for item in json_data['results']:
        results.append({
            "id": item['bgg_id'],
            "name": item['name'],
            "image_url": item['image_url'][0] if len(item['image_url']) > 0 else None,
            "year": item['year'],
            "description": item['description'],
            "url": item['url']
        })

    return results 