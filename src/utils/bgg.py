import requests
from xml.etree import ElementTree as ET

BGG_BASE_URL = 'https://boardgamegeek.com/xmlapi2'

def search(query):
    response = requests.get(f"{BGG_BASE_URL}/search?query={query}")
    root = ET.fromstring(response.content)

    results = []
    for item in root.findall("item"):
        game_id = item.get("id")
        title = item.find("name").get("value")
        year = item.find("yearpublished").get("value") if item.find("yearpublished") is not None else "Unknown"
        results.append({"id": game_id, "title": title, "year": year})

    return results

