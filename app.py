
import flask
from flask import Flask, flash, request, render_template
from spotipy_client.__pycache__.spotipy_client import SpotipyClient

REDIRECT_URI="http://127.0.0.1:5000/api_callback"
SCOPE="playlist-modidy-private,playlist-modify-public,user-top-read"

app = Flask(__name__)
#create secret key to print thing in screen
app.secret_key=b'_kdfhvkfd\n\xec]/'

@app.route("/",methods=["GET","POST"])
def client_auth_form():
    #allows authentication in webserver 
    if request.method=="POST":
        #request information introduced in web formulary
        CLI_ID=request.form["cl_id"]
        CLI_SEC=request.form["cl_secret"]
        USERNAME=request.form["username"]

        sp = SpotipyClient(CLI_ID,CLI_SEC,USERNAME,REDIRECT_URI,SCOPE)
        sp.create_recommended_playlist()
        flash("Playlist created on Spotify, enjoy!")
    return render_template("index.html")
if __name__ == "__main__":
    app.run()
