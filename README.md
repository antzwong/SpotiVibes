# Spotify Playlist Rediscovery

This project helps people curate their playlists by rediscovering songs from all their playlists and picks those which best fit their mood.

## Description

Oftentimes our playlists remain static and overtime we'll forget about songs at the bottom of our playlists because we never get to them. Our application asks users for their mood, retrieves all the songs in their spotify playlists, and picks the ones which will best fit their mood. 


## Installation

Clone the repository onto your local machine. You will need to create an application on spotify [here](https://developer.spotify.com/dashboard/) to retrieve your credentials. While in the developer dashboard, in the settings, set the callback URL to http://localhost:8888/callback. In SpotifyUpdater>authorization_code>app.js, input your credentials into the appropriate fields at the top of the file. Next, navigate to the app.js folder and run 

$node app.js

This will start the application which you can access by going to localhost:8888


## Technicals

Developed using Node.js, Python (flask), HTML, GCP- Natural Language Client Library. 