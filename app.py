
from flask import Flask, flash, request, render_template
from spotipy_client import *

REDIRECT_URI="http://localhost:8888/callback/"
SCOPE="playlist-modify-public,user-top-read"

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
    #from waitress import serve
    #serve(app,host="0.0.0.0",port=8080)
    app.run()
