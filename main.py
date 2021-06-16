from spotify_manager import DJ
from dotenv import load_dotenv
import os
load_dotenv()

if __name__ == "__main__":
    redirect_url = 'http://localhost'

    dj = DJ(os.getenv('USER'), os.getenv('ID'), os.getenv('SECRET'), redirect_url)
    artists = []
    with open('recommended.txt', 'r') as fn:
        artists=[a.strip('\n') for a in fn.readlines()]

    name = 'GoodSongs'
    # dj.playlist.create_playlist(name)
    # dj.add_artist_top_to_playlist(name, artists)

    dj.user.print_user_top_tracks(10)
    dj.user.print_user_top_artists(10)