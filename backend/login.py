# Example script for how to login using Spotify authentication. 
# Note that you would need to setup a .env file during development.

from dotenv import dotenv_values
import requests
import logging

config = dotenv_values(".env")

client_id = config["CLIENT_ID"]
client_secret = config["CLIENT_SECRET"]

logging.info(client_id)

url = "https://accounts.spotify.com/api/token"
params = {"grant_type": "client_credentials", "client_secret": client_secret, "client_id": client_id}
headers={"Content-Type": "application/x-www-form-urlencoded"}
response = requests.post(url, params=params, headers=headers)
logging.info(response.status_code)
logging.info(response.headers)
logging.info(response.json())
