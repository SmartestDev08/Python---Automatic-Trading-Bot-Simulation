import requests
import os
from dotenv import load_dotenv

def get_todays_info():
    load_dotenv()

    url = "https://realstonks.p.rapidapi.com/TSLA"

    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST")
    }

    response = requests.get(url, headers=headers)
    response = response.json()

    return response