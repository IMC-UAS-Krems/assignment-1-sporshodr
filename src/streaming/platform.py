"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""
from _pytest.main import Session
from datetime import datetime, timedelta
from streaming.albums import Album
from streaming.artists import Artist
from streaming.playlists import Playlist, CollaborativePlaylist
from streaming.tracks import Track, Song
from streaming.users import User, PremiumUser, FamilyMember


class StreamingPlatform:
    def __init__(self, name:str):
        self.name = name
        self._catalogue = {}
        self._users = {}
        self._artists = {}
        self._albums = {}
        self._playlists = {}
        self._sessions = []

    def add_track(self, track:Track):
        self._catalogue[track.track_id] = track

    def add_user(self, user:User):
        self._users[user.user_id] = user

    def add_artist(self, artist:Artist):
        self._artists[artist.artist_id] = artist

    def add_album(self, album:Album):
        self._albums[album.album_id] = album

    def add_playlist(self, playlist:Playlist):
        self._playlists[playlist.playlist_id] = playlist

    def record_session(self, session:Session):
        self._sessions.append(session)

    def get_track(self, track_id:str):
        return self._catalogue.get(track_id)

    def get_user(self, user_id:str):
        return self._users.get(user_id)

    def get_artist(self, artist_id:str):
        return self._artists.get(artist_id)

    def get_album(self, album_id:str):
        return self._albums.get[album_id]

    def all_users(self):
        return list(self._users.values())

    def all_tracks(self):
        return list(self._catalogue.values())

    #Query 1
    def total_listening_time_minutes(self,start: datetime, end: datetime) -> float:
        total_seconds = 0
        for session in self._sessions:
            if start <= session.timestamp <= end:
                total_seconds += session.duration_listened_seconds
        return total_seconds / 60

    #Query 2
    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        cutoff = datetime.now() - timedelta(days=days)

        premium_users = []
        for user in self._users.values():
            if isinstance(user, PremiumUser):
                premium_users.append(user)

        if len(premium_users) == 0:
            return 0

        total = 0

        for user in premium_users:
            unique_tracks = []

            for session in self._sessions:
                if session.user == user and session.timestamp >= cutoff:
                    if session.track.track_id not in unique_tracks:
                        unique_tracks.append(session.track.track_id)

            total += len(unique_tracks)

        return total / len(premium_users)

    #Query 3
    def track_with_most_distinct_listeners(self) -> Track | None:
        if len(self._sessions) == 0:
            return None

        track_listeners = {}

        for session in self._sessions:
            track = session.track
            user_id = session.user.user_id

            if track not in track_listeners:
                track_listeners[track] = []

            if user_id not in track_listeners[track]:
                track_listeners[track].append(user_id)

        best_track = None
        max_count = 0

        for track in track_listeners:
            count = len(track_listeners[track])
            if count > max_count:
                max_count = count
                best_track = track

        return best_track
    #Query 4
    def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
        data = {}

        for session in self._sessions:
            user_type = type(session.user).__name__

            if user_type not in data:
                data[user_type] = []

            data[user_type].append(session.duration_listened_seconds)

        result = []

        for user_type in data:
            durations = data[user_type]
            avg = sum(durations) / len(durations)
            result.append((user_type, float(avg)))

        # sort manually (descending)
        for i in range(len(result)):
            for j in range(i + 1, len(result)):
                if result[j][1] > result[i][1]:
                    result[i], result[j] = result[j], result[i]

        return result

    #Query 5
    def total_listening_time_underage_sub_users_minutes(self,age_threshold: int = 18) -> float:
        total = 0

        for session in self._sessions:
            user = session.user

            if isinstance(user, FamilyMember) and user.age < age_threshold:
                total += session.duration_listened_seconds

        return total / 60

    #Query 6
    def top_artists_by_listening_time(self,n: int = 5) -> list[tuple[Artist, float]]:
        artist_time = {}

        for session in self._sessions:
            track = session.track

            if isinstance(track, Song):
                artist = track.artist

                if artist not in artist_time:
                    artist_time[artist] = 0

                artist_time[artist] += session.duration_listened_seconds

        result = []

        for artist in artist_time:
            minutes = artist_time[artist] / 60
            result.append((artist, minutes))

        # manual sort descending
        for i in range(len(result)):
            for j in range(i + 1, len(result)):
                if result[j][1] > result[i][1]:
                    result[i], result[j] = result[j], result[i]

        return result[:n]

    #Query 7
    def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
        user = self.get_user(user_id)

        if user is None:
            return None

        genre_time = {}
        total = 0

        for session in self._sessions:
            if session.user.user_id == user_id:
                genre = session.track.genre

                if genre not in genre_time:
                    genre_time[genre] = 0

                genre_time[genre] += session.duration_listened_seconds
                total += session.duration_listened_seconds

        if total == 0:
            return None

        best_genre = None
        max_time = 0

        for genre in genre_time:
            if genre_time[genre] > max_time:
                max_time = genre_time[genre]
                best_genre = genre

        percentage = (max_time / total) * 100

        return (best_genre, percentage)

    #Query 8
    def collaborative_playlists_with_many_artists(self,threshold: int = 3) -> list[CollaborativePlaylist]:
        result = []

        for playlist in self._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                artists = []

                for track in playlist.tracks:
                    if isinstance(track, Song):
                        if track.artist not in artists:
                            artists.append(track.artist)

                if len(artists) > threshold:
                    result.append(playlist)

        return result
    #Query 9
    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        normal = []
        collaborative = []

        for playlist in self._playlists.values():
            if type(playlist) is Playlist:
                normal.append(len(playlist.tracks))
            elif isinstance(playlist, CollaborativePlaylist):
                collaborative.append(len(playlist.tracks))

        result = {}

        if normal:
            result["Playlist"] = sum(normal) / len(normal)
        else:
            result["Playlist"] = 0.0

        if collaborative:
            result["CollaborativePlaylist"] = sum(collaborative) / len(collaborative)
        else:
            result["CollaborativePlaylist"] = 0.0

        return result
    #Query 10
    def users_who_completed_albums(self) -> list[tuple[User, list[str]]]:
        result = []

        for user in self._users.values():
            listened_track_ids = {
                session.track.track_id
                for session in self._sessions
                if session.user == user
            }

            completed_album_titles = []

            for album in self._albums.values():
                if not album.tracks:
                    continue

                album_track_ids = {track.track_id for track in album.tracks}

                if album_track_ids.issubset(listened_track_ids):
                    completed_album_titles.append(album.title)

            if completed_album_titles:
                result.append((user, completed_album_titles))

        return result