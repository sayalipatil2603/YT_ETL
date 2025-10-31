import requests  #Python libraries for making HTTP requests
import json  #Built-in Python module that lets you work with JSON data (like API responses).
import os
from dotenv import load_dotenv  

load_dotenv(dotenv_path="./.env")  #loads data from .env

API_KEY = os.getenv("API_KEY")  #reads the API_KEY value
CHANNEL_HANDLE = "MrBeast"

def get_playlist_id():

    try: 

        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)   #Retrieve data from a server (read-only), it stores the data plus the response info in response

        #print(response)  #shows the status of the request not the data

        response.raise_for_status() #Do nothing if the request was successful (status code 200–299). Raise an error (requests.exceptions.HTTPError) if the status code indicates a failure (400 or 500 series).

        data = response.json()  #converts json into python dictionary
        # print(json.dumps(data, indent=4))  #converts your Python dictionary back into a formatted JSON string for easy reading. indent=4 adds indentation so the structure is clear.  4 spaces per level

        channel_items = data["items"][0]  #The items key contains a list of channel results. [0] gets the first channel
        channel_playlistsId = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]

        print(channel_playlistsId)

        return channel_playlistsId

    except requests.exceptions.RequestException as e:
        raise e
    
if __name__ == "__main__": #is to make sure that some code only runs when you run the file directly,and does not run when the file is imported into another file.
    get_playlist_id()
