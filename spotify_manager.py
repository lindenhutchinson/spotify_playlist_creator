import spotipy
import spotipy.util as util


class DJ:
    def __init__(self, username, client_id, client_secret, redirect_uri='http://localhost'):
        self.username = username
        self.sp = spotipy.Spotify(auth=self.get_token(
            username, client_id, client_secret, redirect_uri))
        self.playlist = Playlist(self.sp, username)
        self.user = User(self.sp, username)
        self.artist = Artist(self.sp, username)

    def get_token(self, username, client_id, client_secret, redirect_uri, scope='playlist-modify-public user-library-modify user-top-read'):
        return util.prompt_for_user_token(
            self.username,
            scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )

    def get_artists_in_playlist(self, name):
        print("Finding the artists in playlist {}".format(name))
        playlist = self.playlist.get_playlist_fields(name)
        artist_list = []
        for track in playlist['tracks']['items']:
            if track['track']['artists'][0]['name'] in artist_list:
                continue

            artist_list.append(track['track']['artists'][0]['name'])

        return artist_list

    def add_artist_top_to_playlist(self, playlist_name, artist_names):
        print("Adding {} artists' top songs to a playlist".format(len(artist_names)))
        playlist = self.playlist.get_playlist(playlist_name)
        track_ids = []
        for name in artist_names:
            tracks = self.artist.get_artist_top_tracks(name)
            if tracks:
                for track in tracks:
                    track_ids.append(track['id'])

        self.playlist.add_tracks_to_playlist(playlist['id'], track_ids)


class BaseSpotify:
    def __init__(self, sp, username):
        self.sp = sp
        self.username = username


class Playlist(BaseSpotify):
    def get_playlists(self):
        return self.sp.user_playlists(self.username)

    def remove_tracks_from_playlist(self, playlist_id, ids):
        return self.sp.user_playlist_remove_all_occurrences_of_tracks(self.username, playlist_id, ids)

    def add_tracks_to_playlist(self, playlist_id, tracks):
        if len(tracks) > 100: # you can send a maximum of 100 tracks per request
            self.sp.user_playlist_add_tracks(self.username, playlist_id, tracks[:100])
            return self.add_tracks_to_playlist(playlist_id, tracks[100:])
        return self.sp.user_playlist_add_tracks(self.username, playlist_id, tracks)

    def create_playlist(self, name):
        self.sp.user_playlist_create(self.username, name)

    def get_playlist_fields(self, name):
        playlist = self.get_playlist(name)
        return self.sp.playlist(playlist['id'], fields="tracks,next")

    def get_playlist(self, name):
        playlists = self.sp.user_playlists(self.username)
        playlist = [p for p in playlists['items'] if p['name'] == name]

        return playlist[0] if len(playlist) else None


class User(BaseSpotify):
    def get_user_top_artists(self, num):
        ranges = {'short_term': [], 'medium_term': [], 'long_term': []}
        for r, tracks in ranges.items():
            results = self.sp.current_user_top_artists(time_range=r, limit=num)
            for item in results['items']:
                tracks.append(item)

        return ranges
    def get_user_top_tracks(self, num):
        ranges = {'short_term': [], 'medium_term': [], 'long_term': []}
        for r, tracks in ranges.items():
            results = self.sp.current_user_top_tracks(time_range=r, limit=num)
            for item in results['items']:
                tracks.append(item)

        return ranges

    def print_user_top_tracks(self, num):
        print(f"Top {num} songs for {self.username}\n")
        track_list = self.get_user_top_tracks(num)

        for r, tracks in track_list.items():
            print(f"{r}\n")
            for i, track in enumerate(tracks):
                print(f"{i+1} {track['name']} - {track['artists'][0]['name']}")
            print("\n")

    def print_user_top_artists(self, num):
        print(f"Top {num} artists for {self.username}")
        artist_list = self.get_user_top_artists(num)

        for r, artists in artist_list.items():
            print(f"{r}\n")
            for i, artist in enumerate(artists):
                print(f"{i+1} {artist['name']}")
            print("\n")



class Artist(BaseSpotify):
    def get_artist(self, name):
        results = self.sp.search(q='artist:' + name, type='artist')
        items = results['artists']['items']
        if len(items) > 0:
            return items[0]
        else:
            return None

    def get_artist_top_tracks(self, name):
        artist = self.get_artist(name)
        if artist:
            print(f"\tGot {name}")
            return self.sp.artist_top_tracks(artist['uri'])['tracks']
        else:
            print(f"Couldn't find an artist called {name}")


    def get_recommended_for_artist(self, name):
        artist = self.get_artist(name)
        results = self.sp.recommendations(seed_artists=[artist['id']])
        return results['tracks']

    def print_recommended_for_artist(self, name):
        results = self.get_recommended_for_artist(name)
        for track in results['tracks']:
            print('Recommendation: %s - %s',
                  track['name'], track['artists'][0]['name'])
