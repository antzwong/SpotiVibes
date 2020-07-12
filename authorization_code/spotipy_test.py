import re
import config
import json
import typing
import random
from google.cloud import language_v1
from google.cloud.language_v1 import enums
from typing import List, Dict
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os
from tempfile import mkdtemp
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/callback", methods=["GET", "POST"])

def emotion():
    if request.method == "POST":
        print("****8")
        emotion = request.form.get("emotion")
        return emotion

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def show_tracks(results):
    for i, item in enumerate(results['items']):
        track = item['track']
        print(
            "   %d %32.32s %s" %
            (i, track['artists'][0]['name'], track['name']))

def find_tracks_from_playlists(sp: object) -> List:
    
    # return a json of all user playlists
    playlists = sp.current_user_playlists()

    # finds the URIs for the playlists of user
    playlist_uris = []
    for playlist in playlists['items']:
        playlist_uris.append(playlist['uri'])

    # finds all tracks inside a user's playlist
    tracks = []
    for playlist_uri in playlist_uris:
        playlist_tracks = sp.playlist_tracks(playlist_uri, limit = 100)
        for track in playlist_tracks['items']:
            tracks.append(track['track']['uri'])
    
    track_dict = {} # maybe try a another one where tracks are batch queryed 
    for track in batch(tracks, n = 100):
        track_feature = sp.audio_features(track)
        for feature in track_feature:
            track_dict[feature['uri']] = feature

    return track_dict


def is_pos_senti(text_content: str) -> bool:
    client = language_v1.LanguageServiceClient.from_service_account_json("../google_api.json")

    type_ = enums.Document.Type.PLAIN_TEXT

    language = "en"
    document = {"content": text_content, "type": type_, "language": language}

    encoding_type = enums.EncodingType.UTF8

    response = client.analyze_sentiment(document, encoding_type=encoding_type)
    if(response.document_sentiment.score > 0):
        return True
    else:
        return False
   

if __name__ == '__main__':
    
    
    scope = 'playlist-read-private user-modify-playback-state'
    username = 'tmqeyde427wuvgrv4o3j59s8g'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, username = username))

    track_dict = find_tracks_from_playlists(sp)
    happy_list = ['happy', 'excited']
    dancey_list = ['dance', 'hype']

    emotion=input("Hi, I'm called SpotiVibes, the app that queues up songs to match your feelings. How do you feel today? ") 
    
    # spotify must be playing from an active device for this to work
    if any(term in emotion for term in happy_list):
        print('Glad to hear youre feeling happy today!')
        for key, value in sorted(track_dict.items(), key=lambda x: random.random()):
            if(value['valence'] > 0.7 and value['energy'] > 0.7):
                sp.add_to_queue(key)
                break
    elif any(term in emotion for term in dancey_list):
        print('I can tell youre pretty excited today. Lets dance owo')
        for key, value in sorted(track_dict.items(), key=lambda x: random.random()):
            if(value['danceability'] > 0.7 and value['energy'] > 0.7):
                sp.add_to_queue(key)
                break
    elif(is_pos_senti(emotion)):
        print('Glad to hear youre feeling happy today!')
        for key, value in sorted(track_dict.items(), key=lambda x: random.random()):
            if(value['valence'] > 0.7 and value['energy'] > 0.7):
                sp.add_to_queue(key)
                break
    else:
        print('Okay, heres a calming song to help soothe your day')
        for key, value in sorted(track_dict.items(), key=lambda x: random.random()):
            if(value['valence'] < 0.3 and value['energy'] < 0.3 and value['tempo']<120):
                sp.add_to_queue(key)
                break
    sp.next_track()
    

