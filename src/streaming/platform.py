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
from streaming.playlists import Playlist
from streaming.tracks import Track
from streaming.users import User


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
    def total_listening_time_minutes(start: datetime, end: datetime) -> float:
        total_seconds = 0
        for session in self._sessions:
            if start <= session.timestamp <= end:
                total_seconds += session.duration_listened_seconds
        return total_seconds / 60

    #Query 2
    def avg_unique_tracks_per_premium_user(days: int = 30) -> float:
        premium_users = [
            user for user in self._users.values()
            if type(user) is PremiumUser
        ]

        if not premium_users:
            return 0.0

        cutoff = datetime.now() - timedelta(days=days)
        total_unique = 0

        for user in premium_users:
            unique_track_ids = {
                session.track.track_id
                for session in self._sessions
                if session.user == user and session.timestamp >= cutoff
            }
            total_unique += len(unique_track_ids)

        return total_unique / len(premium_users)

    #Query 3
    def track_with_most_distinct_listeners() -> Track | None:
        if not self._sessions:
            return None

        listeners_by_track = {}

        for session in self._sessions:
            track = session.track
            user_id = session.user.user_id

            if track not in listeners_by_track:
                listeners_by_track[track] = set()

            listeners_by_track[track].add(user_id)

        return max(listeners_by_track, key=lambda track: len(listeners_by_track[track]))

    #Query 4
    def avg_session_duration_by_user_type() -> list[tuple[str, float]]:
        grouped = {}

        for session in self._sessions:
            type_name = type(session.user).__name__

            if type_name not in grouped:
                grouped[type_name] = []

            grouped[type_name].append(session.duration_listened_seconds)

        result = []
        for type_name, durations in grouped.items():
            average = sum(durations) / len(durations)
            result.append((type_name, float(average)))

        result.sort(key=lambda item: item[1], reverse=True)
        return result

    #Query 5
    def total_listening_time_underage_sub_users_minutes(age_threshold: int = 18) -> float:
        total_seconds = 0

        for session in self._sessions:
            user = session.user
            if isinstance(user, FamilyMember) and user.age < age_threshold:
                total_seconds += session.duration_listened_seconds

        return total_seconds / 60

    #Query 6
    def top_artists_by_listening_time(n: int = 5) -> list[tuple[Artist, float]]:
        artist_totals = {}

        for session in self._sessions:
            track = session.track

            if isinstance(track, Song):
                artist = track.artist
                if artist not in artist_totals:
                    artist_totals[artist] = 0
                artist_totals[artist] += session.duration_listened_seconds

        ranked = sorted(
            [(artist, total_seconds / 60) for artist, total_seconds in artist_totals.items()],
            key=lambda item: item[1],
            reverse=True
        )

        return ranked[:n]

    #Query 7
    def user_top_genre(user_id: str) -> tuple[str, float] | None:
        user = self.get_user(user_id)
        if user is None:
            return None

        user_sessions = [session for session in self._sessions if session.user.user_id == user_id]
        if not user_sessions:
            return None

        genre_totals = {}
        total_seconds = 0

        for session in user_sessions:
            genre = session.track.genre
            if genre not in genre_totals:
                genre_totals[genre] = 0

            genre_totals[genre] += session.duration_listened_seconds
            total_seconds += session.duration_listened_seconds

        top_genre = max(genre_totals, key=genre_totals.get)
        percentage = (genre_totals[top_genre] / total_seconds) * 100

        return (top_genre, percentage)

    #Query 8
    def collaborative_playlists_with_many_artists(threshold: int = 3) -> list[CollaborativePlaylist]:
        result = []

        for playlist in self._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                distinct_artists = {
                    track.artist
                    for track in playlist.tracks
                    if isinstance(track, Song)
                }

                if len(distinct_artists) > threshold:
                    result.append(playlist)

        return result

    #Query 9
    def avg_tracks_per_playlist_type() -> dict[str, float]:
        playlist_counts = []
        collaborative_counts = []

        for playlist in self._playlists.values():
            if type(playlist) is Playlist:
                playlist_counts.append(len(playlist.tracks))
            elif isinstance(playlist, CollaborativePlaylist):
                collaborative_counts.append(len(playlist.tracks))

        return {
            "Playlist": sum(playlist_counts) / len(playlist_counts) if playlist_counts else 0,
            "CollaborativePlaylist": sum(collaborative_counts) / len(
                collaborative_counts) if collaborative_counts else 0,
        }

    #Query 10
    def users_who_completed_albums() -> list[tuple[User, list[str]]]:
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