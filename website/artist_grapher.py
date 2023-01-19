import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect
import json
import time
import pandas as pd


class SpotipyConnection(object):
    sp = None
    def __init__(self,sp,*args,**kwargs) -> None:
        self.sp = sp

    #Gets artist id given artist(natural text)
    def get_artist_id(self,artist): 
        artist_search = self.sp.search(artist)
        itesm = artist_search.get('tracks')
        thign = itesm.get('items')
        for thing in thign:
            aritst_sec = thing.get('artists')
        for element in aritst_sec:
            artist_id = element.get('id')
        return artist_id

    #given list of albums(natural text) removes deluxe, edited and explicit 
    def filter_albums(self,album_list):
        new_album_list = [*set(album_list)]
        for album in new_album_list:
            if (album+' (Deluxe)') in new_album_list:
                removeable_element = album+' (Deluxe)'
                new_album_list.remove(removeable_element)
            if (album+' (Edited Version)') in new_album_list:
                removeable_element = (album+' (Edited Version)')
                new_album_list.remove(removeable_element)
            if (album+' (Explicit Version)') in new_album_list:
                removeable_element = album+' (Explicit Version)'
                new_album_list.remove(removeable_element)
        return new_album_list

    
    def get_albums_by_artist(self,artist_id):
        artist_uri = 'spotify:artist:'+artist_id
        album_list = []
        results = self.sp.artist_albums(artist_uri, album_type='album')
        albums = results['items']
        for i in range(len(albums)):
            album_list.append(albums[i].get('name'))
        return self.filter_albums(album_list)

    #returns id of input album(natural text)
    def get_album_id(self,name):
        album = self.sp.search(name,type='album',limit=1)
        return album.get('albums').get('items')[-1].get('id')

#gets song ids from albumID
    def get_songs_id(self,album): 
        album = self.sp.album_tracks(album)
        album_songs_items = album.get('items')
        id_list= []
        for thing in album_songs_items:
            id = thing.get('id')
            id_list.append(id)
        return id_list

    #parses json for pop
    def get_popularity(self,id_list):
        song_dict = []
        for id in id_list:
            id_info = self.get_track(id)
            song_dict.append(id_info)
            #print(id_info)
        song_dict = list(song_dict)
        return song_dict
#This gets the populartiy and names of each song, pop the value song the key
#put in list of ids from above functions
    def get_song_pop(self,album):
        pop_song_dict = {}
        pop_list = []
        song_list = []
        for thing in album:
            if (type(thing) != str):
                pop_list.append(thing.get('popularity'))
                song_list.append(thing.get('name'))
 
        for song,pop in zip(song_list,pop_list):
            pop_song_dict[song] = pop
        return pop_song_dict

    def graph_pop_albums(self,stats):
        pass

    def graph_pop_albums_full(self,artist_name):
        albums = self.get_albums_by_artist(self.get_artist_id(artist_name))
        album_pop = {}
        for album in albums:
            pop_sum = sum(self.get_song_pop(self.get_popularity(self.get_songs_id(self.get_album_id(album)))).values())
            album_pop[album] = pop_sum

        
        self.graph_pop_songs(album_pop)
        return album_pop
    

    def graph_pop_songs_full(self,query):
        self.graph_pop_songs(self.get_song_pop(self.get_popularity(self.get_songs_id(self.get_album_id(query)))))
        
    #from album(natural text) gets cover,popularity,artist_id,artist_name
    def get_album_stuff(self,album):
        album_dict = self.sp.album(self.get_album_id(album))
        artist_name=album_dict['artists'][0]['name']
        artist_id = album_dict['artists'][0]['id']
        popularity = album_dict['popularity']
        image_link = album_dict['images'][0]['url']

        return [artist_id,artist_name,popularity,image_link]