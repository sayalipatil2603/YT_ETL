import requests  #Python libraries for making HTTP requests
import json  #Built-in Python module that lets you work with JSON data (like API responses).
import os
from dotenv import load_dotenv  
from datetime import date

load_dotenv(dotenv_path="./.env")  #loads data from .env

API_KEY = os.getenv("API_KEY")  #reads the API_KEY value
CHANNEL_HANDLE = "MrBeast"
Max_Results = 50   #max videos per page is 50 for youtube


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



def get_video_ids(playlist_id):

    video_ids = []
    PageToken = None
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={Max_Results}&playlistId={playlist_id}&key={API_KEY}" 

    try:
        while True:

            url = base_url
            if PageToken:
                url+= f"&PageToken={PageToken}"  #here the next page token will be replaced and the code will run

            response = requests.get(url)   #Retrieve data from a server (read-only), it stores the data plus the response info in response

            response.raise_for_status() #Do nothing if the request was successful (status code 200–299). Raise an error (requests.exceptions.HTTPError) if the status code indicates a failure (400 or 500 series).

            data = response.json()  

            for item in data.get('items', []):   #if it does not find item it returns an empty list
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
    
            PageToken = data.get('nextPageToken') #this will get the next page token

            if not PageToken:   #if there is no next page 
                break

        return video_ids
    
    except requests.exceptions.RequestException as e:
        raise e


 
def extract_video_data(video_ids):
    extracted_data = []

    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id: video_id + batch_size]  #Instead of returning all results at once (like return), it pauses the function and returns one item (here, a batch of IDs) each time.
            #maximum size is 50 therefore batch will be of 50
    try:
        for batch in batch_list(video_ids, Max_Results):  #first executes for first batch then second and so on..
            video_ids_str = ",".join(batch)  #",".join(batch) converts the list ['id1','id2'] → 'id1,id2'

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"

            response = requests.get(url)   #Retrieve data from a server (read-only), it stores the data plus the response info in response

            response.raise_for_status() #Do nothing if the request was successful (status code 200–299). Raise an error (requests.exceptions.HTTPError) if the status code indicates a failure (400 or 500 series).

            data = response.json()

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    "video_id": video_id,
                    "title": snippet['title'],
                    "publishedAt": snippet['publishedAt'],
                    "duration": contentDetails['duration'],
                    "viewCount": statistics.get('viewCount', None),
                    "likeCount": statistics.get('likeCount', None),
                    "commentCount": statistics.get('commentCount', None)
                }  

                extracted_data.append(video_data)  

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e 

def save_to_json(extracted_data):
    file_path = f"./data/YT_data_{date.today()}.json"   #the folder where the file will be saved (relative to your current working directory).YT_data_{date.today()}.json → the file name, which includes today’s date

    with open(file_path, "w", encoding="utf-8") as json_outfile:   #Opens the file at file_path in write mode ("w")
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)
        

if __name__ == "__main__": #is to make sure that some code only runs when you run the file directly,and does not run when the file is imported into another file.
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)

'''encoding="utf-8" ensures Unicode characters (like emojis, special characters) are handled correctly.
        with → a context manager that automatically closes the file after writing.
        json_outfile → a file object we can write to '''
'''extracted_data → the Python object to convert to JSON.
        json_outfile → the file to write the JSON string into.
        indent=4 → pretty-print with 4 spaces per level.
        ensure_ascii=False → keeps Unicode characters intact (doesnt escape them as \uXXXX).'''    