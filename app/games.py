import requests
from flask import current_app

def get_games_list(page=1, page_size=20, search_query=None):
    """Fetch a list of games from RAWG API"""
    url = "https://api.rawg.io/api/games"
    params = {
        'key': current_app.config['RAWG_API_KEY'],
        'page': page,
        'page_size': page_size,
        'ordering': '-rating'  # Get highest rated games first
    }
    
    if search_query:
        params['search'] = search_query
    
    response = requests.get(url, params=params)
    return response.json() if response.ok else None

import requests
from flask import current_app

def get_games_list(page=1, page_size=20, search_query=None):
    """Fetch a list of games from RAWG API"""
    url = "https://api.rawg.io/api/games"
    params = {
        'key': current_app.config['RAWG_API_KEY'],
        'page': page,
        'page_size': page_size,
        'ordering': '-rating'  # Get highest rated games first
    }
    
    if search_query:
        params['search'] = search_query
    
    response = requests.get(url, params=params)
    return response.json() if response.ok else None

def get_game_details(game_id):
    """Fetch details for a specific game"""
    url = f"https://api.rawg.io/api/games/{game_id}"
    params = {
        'key': current_app.config['RAWG_API_KEY']
    }
    
    response = requests.get(url, params=params)
    return response.json() if response.ok else None