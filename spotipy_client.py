import spotipy
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
        self.client_id=client_id
        self.client_secret=client_secret
        self.username=username
        self.redirect_uri=redirect_uri
        self.scope=scope
    def client_auth(self):
        '''spotify's API authetication'''
        token=util.prompt_for_user_token(self.username,self.scope,self.client_id,self.client_secret,self.redirect_uri)
        self.client=spotipy.Spotify(auth=token)
    def get_top_tracks(self):
        top_tracks=self.client.current_user_top_tracks(time_range="short_term",limit=20)
        return top_tracks

    