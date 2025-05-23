# This file contains functions that are used in the bot.
# It includes functions for getting truths, dares, would you rather questions, memes, insults, and converting Steam URLs to SteamID64.

import requests, random

from lists import logTypes

from datetime import datetime as dt

from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()
# Load the token from the .env file
STEAM_API_KEY = os.getenv("STEAM_API_KEY")


# Main functions
def Log(type, message):
    try:
        print(f"[{dt.now().strftime('%H:%M:%S')}] [ {logTypes[type]} ] {message}")
    except Exception as e:
        print(f"Error logging message: {e}")

def get_truth():
    # Send a GET request to the API
    response = requests.get("https://api.truthordarebot.xyz/v1/truth")

    # Parse the JSON response
    data = response.json()

    # Extract the truth question
    question = data["question"]

    # Return the truth question to the function
    return(question)

def get_dare():
    # Send a GET request to the API
    response = requests.get("https://api.truthordarebot.xyz/v1/dare")

    # Parse the JSON response
    data = response.json()

    # Extract the truth question
    question = data["question"]

    # Return the truth question to the function
    return(question)

def get_wyr():
    # Send GET request to the API
    response = requests.get("https://api.truthordarebot.xyz/v1/wyr")

        # Parse the JSON response
    data = response.json()

    # Extract the truth question
    question = data["question"]

    # Return the truth question to the function
    return(question)

def get_funny():
    # Send a GET request to the API
    response = requests.get("https://api.humorapi.com/memes")
    
    # Parse the JSON response
    data = response.json()

    # Extract the 'memes' array from the JSON
    memes = data["memes"]
    
    # Randomly choose a meme from the array
    random_meme = random.choice(memes)

    # Get the URL of the meme
    meme_url = random_meme["url"]

    return meme_url

def get_insult():
    response = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json")
    data = response.json()
    insult = data.get("insult")
    return insult

def get_steamid64(vanity_url):
    api_key = STEAM_API_KEY  # Replace with your actual Steam API key
    base_url = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/'
    params = {
        'key': api_key,
        'vanityurl': vanity_url
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data['response']['success'] == 1:
        return data['response']['steamid']
    else:
        return None

def convert_url(url):
    api_key = STEAM_API_KEY  # Replace with your actual Steam API key
    if 'steamcommunity.com/profiles/' in url:
        # Extract the SteamID64 directly from the URL
        steamid64 = url.split('/')[-1] if url.endswith('/') else url.split('/')[-1]
    elif 'steamcommunity.com/id/' in url:
        # Extract the vanity URL and resolve to SteamID64
        vanity_url = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
        steamid64 = get_steamid64(vanity_url)
    else:
        steamid64 = None
    
    return steamid64

def hours_to_seconds(hours):
    return hours * 60 * 60