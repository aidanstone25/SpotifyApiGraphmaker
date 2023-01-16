import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect, flash,render_template,Blueprint
import json
import time
import pandas as pd
import sys
from . import popularity_graph
from .popularity_graph import get_song_pop,graph_pop_songs


auth = Blueprint('auth', __name__)

@auth.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@auth.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/home")

@auth.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/authorize')

@auth.route('/home',methods=['GET','POST'])
def get_all_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        searched_playlist = request.form.get('playlist')
        #store userplaysists in cache if you get tiome
        user_playlists = sp.current_user_playlists()
        
        user_playlists_dict = {}
        for playlist in user_playlists['items']:         
            user_playlists_dict[playlist['name']] = playlist['id'] 
        
        #return sp.user_playlist_tracks(playlist_id='4keX53IMfZdgD6xhDfWDtk')
        try:
            playlist_id = searched_playlist[searched_playlist]
            playlist = sp.user_playlist_tracks(playlist_id=playlist_id)
            song_dict={}
            for song in playlist['items']:
                song_dict[song['name']] = song['popularity']
            return [song_dict,searched_playlist,'uauauhs']
        except:
            pass
        if searched_playlist in user_playlists_dict.keys():
            song_dict= get_song_pop(sp.user_playlist_tracks(playlist_id=user_playlists_dict[searched_playlist]))
            graph_pop_songs(song_dict)
            return song_dict
            #api_spotipy.return_user_pi(sp.user_playlist_tracks(playlist_id=user_playlists_dict[searched_playlist]))
        #return str(sp.user_playlist_tracks(playlist_id=user_playlists_dict[searched_playlist]))
        return song_dict
    return render_template('search.html')


@auth.route('/album',methods=['GET','POST'])
def album():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        searched_playlist = request.form.get('album')
        #store userplaysists in cache if you get tiome


        user_playlists = sp.current_user_playlists()
        user_playlists_dict = {}
        for playlist in user_playlists.values():
            user_playlists_dict[playlist['name']] = playlist['id']
        if searched_playlist in user_playlists_dict.keys():
            pass
            #api_spotipy.return_user_pi(sp.user_playlist_tracks(playlist_id=user_playlists_dict[searched_playlist]))
        return str(sp.user_playlist_tracks(playlist_id=user_playlists_dict[searched_playlist]))
    return render_template('search.html')


# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="4e3d2cc9dfe2450890181834312c968d",
            client_secret="4bdae51c78e84281ba04e1658a0d41f5",
            redirect_uri="http://127.0.0.1:5000/authorize",
            scope="playlist-read-private")

#app.run(debug=True)