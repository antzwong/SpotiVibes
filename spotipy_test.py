import re
import config
import spotipy
import json
import typing
import random
from google.cloud import language_v1
from google.cloud.language_v1 import enums
from typing import List, Dict
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

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
    '''
    for track in tracks:
        track_feature = sp.audio_features(track)
        track_dict[track] = track_feature
    '''
    for track in batch(tracks, n = 100):
        track_feature = sp.audio_features(track)
        for feature in track_feature:
            track_dict[feature['uri']] = feature

    return track_dict


def is_pos_senti(text_content: str) -> bool:
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """
    client = language_v1.LanguageServiceClient.from_service_account_json("google_api.json")

    # text_content = 'I am so happy and joyful.'

    # Available types: PLAIN_TEXT, HTML
    type_ = enums.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = enums.EncodingType.UTF8

    response = client.analyze_sentiment(document, encoding_type=encoding_type)
    # Get overall sentiment of the input document
    print(u"Document sentiment score: {}".format(response.document_sentiment.score))
    print(
        u"Document sentiment magnitude: {}".format(
            response.document_sentiment.magnitude
        )
    )
    if(response.document_sentiment.score > 0):
        return True
    else:
        return False
   

if __name__ == '__main__':
    
    
    scope = 'playlist-read-private user-modify-playback-state'
    username = 'tmqeyde427wuvgrv4o3j59s8g'
    emotion = 'Im feeling sad'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, username = username))

    track_dict = find_tracks_from_playlists(sp)

    #scope = 'user-modify-playback-state'
    #sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, username = username))
    if(is_pos_senti(emotion)):
        for key, value in sorted(track_dict.items(), key=lambda x: random.random()):
            if(value['valence'] > 0.7 and value['energy'] > 0.7):
                sp.add_to_queue(key)
                break
    else:
        for key, value in sorted(track_dict.items(), key=lambda x: random.random()):
            if(value['valence'] < 0.3 and value['energy'] < 0.3):
                sp.add_to_queue(key)
                break
    sp.next_track()
    

