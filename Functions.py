import requests, random

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