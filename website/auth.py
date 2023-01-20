import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect, flash,render_template,Blueprint
import json
import time
import pandas as pd
from .popularity_graph import get_song_pop,graph_pop_songs
from flask_login import login_user, logout_user,current_user
from . import db
from . models import Albums,User,Artist
from . import artist_grapher
import jsonify


auth = Blueprint('auth', __name__)

#spotify auth, creates local account for database
@auth.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    signed_in_user=sp.current_user()
    user = User.query.filter_by(spotify_user_id=signed_in_user['id']).first()
    if user:
        login_user(user=user,remember=True)
    else:
        new_user = User(spotify_user_id=signed_in_user['id'])
        db.session.add(new_user)
        db.session.commit()
        login_user(user=new_user,remember=True)

    return redirect(auth_url)


#reauthorize
@auth.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/home")


#TODO doesn't work, need to delete session cookie but session.clear() doesn't work
@auth.route('/logout')
def logout():
    s = """
    access_token = session.get('token_info').get('access_token')
    refresh_token = session.get('token_info').get('refresh_token')
    headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/x-www-form-urlencoded',
        }
    data = {
        'refresh_token': refresh_token
    }
    response = requests.post('https://accounts.spotify.com/api/logout', headers=headers, data=data)
    logout_user()
    #session.clear()
     
    return render_template('/loginbutton.html')
    """
    
    logout_user()
    session.clear()
    
    return redirect('/loginbutton')
    

#Redirected when logout
@auth.route('/loginbutton',methods=['GET','POST'])
def loginbutton():
    if request.method == 'POST':
        return redirect('/')
    return render_template('loginbutton.html')

#playlist popularity chart
@auth.route('/home',methods=['GET','POST'])
def get_all_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        searched_playlist = request.form.get('playlist')
        #storef userplaysists in cache if you get tiome
        user_playlists = sp.current_user_playlists()
        
        #TODO store in cache?
        user_playlists_dict = {}
        for playlist in user_playlists['items']:         
            user_playlists_dict[playlist['name']] = playlist['id']         


        if searched_playlist in user_playlists_dict.keys(): 
            song_dict= get_song_pop(sp.user_playlist_tracks(playlist_id=user_playlists_dict[searched_playlist]))
            graph_pop_songs(song_dict)
        else:
            flash('Playlist not found',category='error')
    return render_template('search.html',user=current_user)
#TODO function to change scores
#Rate albums
@auth.route('/album_rating',methods=['GET','POST'])
def album_rating():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        album_name = request.form.get('new_album')
        album_rating = request.form.get('Rating')

        if not album_name or not album_rating:
            flash('Please fill both fields out', category='error')
        else:
            ag = artist_grapher.SpotipyConnection(sp=sp)
            album_id = ag.get_album_id(name=album_name)
            signed_in_user=sp.current_user()
            Album = Albums.query.filter_by(spotify_user_id=signed_in_user['id'],album_id=album_id).first()
            if Album:
                flash('This album is a duplicate',category='error')
            else:
                album_stuff = ag.get_album_stuff(album_name)
                current_user_id = signed_in_user=signed_in_user['id']
                new_album = Albums(album_id = album_id, album=album_name, artist= album_stuff[1],artist_id=album_stuff[0],album_rating=album_rating,album_cover_link=album_stuff[-1],popularity=album_stuff[2],spotify_user_id=current_user_id)
                db.session.add(new_album)
                #urelated, but funny pickup line joe told me: If you're looking for a stud, I got an std, all I need is u
                db.session.commit()
                flash('album added!',category='success')

    return render_template('album_rating.html',user=current_user)

@auth.route('/delete_album',methods=['POST'])
def delete_album():
    album=json.loads(request.data)
    albumID = album['albumID']
    album = Albums.query(album_id = albumID)
    if album:
        if album.user_id == current_user.id:
            db.session.delete(album)
            db.session.commit()
            flash('Album deleted',category='success')
    return None

#Gets the popularity of each album in artists discography
@auth.route('/artist',methods=['GET','POST'])
def artist():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        searched_artist = request.get.form('artist')
        ag = artist_grapher.SpotipyConnection(sp=sp)
        ag.graph_pop_songs_full(query=searched_artist)
    return render_template('album.html')
    
#Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

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

#creates auth token
def create_spotify_oauth():
    return SpotifyOAuth(
            client_id='',
            client_secret='',
            redirect_uri="http://127.0.0.1:5000/authorize",
            scope="playlist-read-private")