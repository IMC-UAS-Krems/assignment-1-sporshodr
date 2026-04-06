"""
tracks.py
---------
Implement the class hierarchy for all playable content on the platform.

Classes to implement:
  - Track (abstract base class)
    - Song
      - SingleRelease
      - AlbumTrack
    - Podcast
      - InterviewEpisode
      - NarrativeEpisode
    - AudiobookTrack
"""
class Track:
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str):
        self.track_id = track_id
        self.title = title
        self.duration_seconds = duration_seconds
        self.genre = genre

    def duration_minutes(self) -> float:
        return self.duration_seconds / 60

class Song(Track):
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist):
        super().__init__(track_id, title, duration_seconds, genre)
        self.artist = artist
1
class Podcast(Track):
    def __init__(self, host: str, description: str):
        super().__init__(track_id, title, duration_seconds, genre)
        self.host = host
        self.description = description

class AudiobookTrack(Track):
    def __init__(self, author: str, narrator: str):
        super().__init__(track_id, title, duration_seconds, genre)
        self.author = author
        self.narrator = narrator

class AlbumTrack(Song):
    def __init__( self,track_id: str,title: str,duration_seconds: int,genre: str,artist,track_number: int,album=None,):
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.track_number = track_number
        self.album = album

class SingleRelease(Song):
    def __init__(self, release_date):
        super().__init__(track_id, title, duration_seconds, genre)
        self.release_date = release_date

class NarrativeEpisode(Podcast):
    def __init__(self, season: int, episode_number: int):
        super().__init__(track_id, title, duration_seconds, genre)
        self.season = season
        self.episode_number = episode_number

class InterviewEpisode(Podcast):
    def __init__(self, guest: str):
        super().__init__(track_id, title, duration_seconds, genre)
        self.guest = guest