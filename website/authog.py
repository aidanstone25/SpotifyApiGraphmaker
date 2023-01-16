from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import json
import time
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import flash, session, request,redirect,url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth


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
    print(code)
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/home")

@auth.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

#TODO
@auth.route('/home')
def get_all_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    plaa = sp.current_user_playlists()
    flash(plaa)
    
    return "done"


# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="8af6619c18ce43ee835d8b0be8999119",
            client_secret="2936ae1ae49946599eb3434a261a85cc",
            redirect_uri=url_for('auth.authorize', _external=True),
            scope="user-library-read")
client_id = '8af6619c18ce43ee835d8b0be8999119'
client_secret = '2936ae1ae49946599eb3434a261a85cc'

s="""client_id="4e3d2cc9dfe2450890181834312c968d,client_secret="4bdae51c78e84281ba04e1658a0d41f5"""