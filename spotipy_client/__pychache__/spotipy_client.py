
import spotipy
import numpy as np
import spotipy.util as util
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import linear_kernel

class SpotipyClient():
    client=None
    client_id=None
    Client_secret=None
    username=None
    redirect_uri="http://localhost:8888"

    def __init__(self,client_id,client_secret,username,redirect_uri,scope):
        self.client_id= client_id
        self.client_secret= client_secret
        self.username= username
        self.redirect_uri= redirect_uri
        self.scope= scope
    
    def client_auth(self):
        '''spotify's API authetication'''
        token=util.prompt_for_user_token(self.username,self.scope,self.client_id,self.client_secret,self.redirect_uri)
        self.client=spotipy.Spotify(auth=token)
    
    def get_top_tracks(self):
        top_tracks=self.client.current_user_top_tracks(time_range="short_term",limit=20)
        return top_tracks
    
    def create_tracks_dataframe(self,top_tracks):
        tracks=top_tracks["items"]
        tracks_ids=[track["id"]for track in tracks]
        audio_features=self.client.audio_features(tracks_ids)
        top_tracks_df=pd.DataFrame(audio_features)
        top_tracks_df=top_tracks_df[["id","danceability","energy", "key", "loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo"]]
        return top_tracks_df

    def get_artists_ids(self,top_tracks):
        ids_artists=[]
        for item in top_tracks["items"]:
            artist_id = item["artists"][0]["id"]
            artist_name=item["items"][0]["name"]
            ids_artists.append(artist_id)
        # filtering repoetitions in artists
        ids_artists=list(set(ids_artists))
        return ids_artists
    
    def get_similar_artists_ids(self,ids_artists):
        ids_similar_artists=[]
        for artist_id in ids_artists:
            artists=self.client.artist_related_artists(artist_id)["artists"]
            for item in artists:
                artist_id=item["id"]
                artist_name=item["name"]
                ids_similar_artists.append(artist_id)
        ids_artists.extend(ids_similar_artists)
        # filtering repetitions
        ids_artists=list(set(ids_artists))
        return ids_artists

    def get_new_releases_artists_ids(self,ids_artists):
        new_releases=self.client.new_releases(limit=20)["albums"]
        for item in new_releases["items"]:
            artist_id =item["artists"][0]["id"] 
            ids_artists.append(artist_id) 
        ids_artists=list(set(ids_artists))  
        return ids_artists
    
    def get_albums_ids(self,ids_artists):
        ids_albums=[]
        for i in ids_artists:
            album =self.client.artist_albums(ids_artists,limit=1)["items"][0]
            ids_albums.append(album["id"])
    
        return ids_albums

    def get_albums_tracks(self,ids_albums):
        ids_tracks=[]
        for id_album in ids_albums:
            album_tracks=self.client.album_tracks(id_album,limit=1)["items"]
            for track in album_tracks:
                ids_tracks.append(track["id"])
        return ids_tracks
    def get_tracks_features(self,ids_tracks):
        ntracks=len(ids_tracks)
        if ntracks>100:
            m=ntracks//100
            n=ntracks%100
            lotes=[None]*(m+1)
            for i in range(m):
                lotes[i]=ids_tracks[i*100:i*100+100]
            if n != 0:
                lotes[i+1]=ids_tracks[(i+1)*100:]
        else:
            lotes=[ids_tracks]

        audio_features=[]
        for lote in lotes:
            features =self.client.audio_features(lote)
            audio_features.append(features)
        audio_features=[item for sublist in audio_features for item in sublist]

        candidates_df=pd.DataFrame(audio_features)
        candidates_df=candidates_df[["id","danceability","energy", "key", "loudness","mode","speechiness","acousticness","instrumentalness","liveness","valence","tempo"]]
        return candidates_df

    def compute_cossim(self,top_tracks_df,candidates_df):
        top_tracks_mtx=top_tracks_df.iloc[:,1:].values
        candidates_mtx=candidates_df.iloc[:,1:].values

        scaler=StandardScaler()
        top_tracks_scaled=scaler.fit_transform(top_tracks_mtx)
        can_scaled=scaler.fit_transform(candidates_mtx)

        top_tracks_norm=np.sqrt((top_tracks_scaled*top_tracks_scaled).sum(axis=1))
        can_norm=np.sqrt((can_scaled*can_scaled).sum(axis=1))

        n_top_tracks=top_tracks_scaled.shape[0]
        n_candidates=can_scaled.shape[0]
        top_tracks=top_tracks_scaled/top_tracks_norm.reshape(n_top_tracks,1)
        candidates=can_scaled/can_norm.reshape(n_candidates,1)

        cos_sim=linear_kernel(top_tracks,candidates)
        return cos_sim
    
    def content_based_filtering(self,pos,cos_sim,ncands,umbral=0.8):
        idx=np.where(cos_sim[pos,:]>=umbral)[0]
        idx=idx[np.argsort(cos_sim[pos,idx])[::-1]]
        if len(idx)>= ncands:
            cands=idx[0:ncands]
        else:
            cands=idx
        return cands
    
    def create_recommended_playlist(self):
        #scope="playlist-modify-public"
        self.client_auth()

        top_tracks=self.get_top_tracks()
        top_tracks_df=self.create_tracks_dataframe(top_tracks)
        ids_artists=self.get_artists_ids(top_tracks)
        ids_artists=self.get_similar_artists_ids(ids_artists)
        ids_artists=self.get_new_releases_artists_ids(ids_artists)
        ids_albums=self.get_albums_ids(ids_artists)
        ids_tracks=self.get_albums_tracks(ids_albums)
        candidates_df=self.get_tracks_features(ids_tracks)
        cos_sim=self.compute_cossim(top_tracks_df,candidates_df)

        ids_top_tracks=[]
        ids_playlist=[]

        for i in range(top_tracks_df.shape[0]):
            ids_top_tracks.append(top_tracks_df["id"][i])

            cands=self.content_based_filtering(i,cos_sim,5,umbral=0.7)

            if len(cands)==0:
                continue
            else:
                for j in cands:
                    id_cand=candidates_df["id"][j]
                    ids_playlist.append(id_cand)

        ids_playlist_dep=[x for x in ids_playlist if x not in ids_top_tracks]
        ids_playlist_dep=list(set(ids_playlist_dep))

        pl=self.client.user_playlist_create(user=self.username,name="Spotipy Recommender Playlist",description="Playlist created based on your top 20 songs")
        self.client.playlist_add_items(pl["id"],ids_playlist_dep)



