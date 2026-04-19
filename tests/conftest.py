"""
conftest.py
-----------
Shared pytest fixtures used by both the public and private test suites.
"""

import pytest
from datetime import date, datetime, timedelta

from streaming.platform import StreamingPlatform
from streaming.artists import Artist
from streaming.albums import Album
from streaming.tracks import (
    AlbumTrack,
    SingleRelease,
    InterviewEpisode,
    NarrativeEpisode,
    AudiobookTrack,
)
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.sessions import ListeningSession
from streaming.playlists import Playlist, CollaborativePlaylist


# ---------------------------------------------------------------------------
# Helper - timestamps relative to the real current time so that the
# "last 30 days" window in Q2 always contains RECENT sessions.
# ---------------------------------------------------------------------------
FIXED_NOW = datetime.now().replace(microsecond=0)
RECENT = FIXED_NOW - timedelta(days=10)   # well within 30-day window
OLD    = FIXED_NOW - timedelta(days=60)   # outside 30-day window


@pytest.fixture
def platform() -> StreamingPlatform:
    """Return a fully populated StreamingPlatform instance."""
    platform = StreamingPlatform("TestStream")

    # ------------------------------------------------------------------
    # Artists
    # ------------------------------------------------------------------
    pixels  = Artist("a1", "Pixels",    genre="pop")
    platform.add_artist(pixels)
    echo = Artist("a2", "Echo", genre="rock")
    platform.add_artist(echo)

    # ------------------------------------------------------------------
    # Albums & AlbumTracks
    # ------------------------------------------------------------------
    dd = Album("alb1", "Digital Dreams", artist=pixels, release_year=2022)
    t1 = AlbumTrack("t1", "Pixel Rain",      180, "pop",  pixels, track_number=1)
    t2 = AlbumTrack("t2", "Grid Horizon",    210, "pop",  pixels, track_number=2)
    t3 = AlbumTrack("t3", "Vector Fields",   195, "pop",  pixels, track_number=3)
    t4 = AlbumTrack("t4", "Rock Song", 200, "rock", echo, track_number=1)
    platform.add_track(t4)
    echo.add_track(t4)
    for track in (t1, t2, t3,t4):
        dd.add_track(track)
        platform.add_track(track)
        pixels.add_track(track)
    platform.add_album(dd)


    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    alice = FreeUser("u1", "Alice",   age=30)
    bob   = PremiumUser("u2", "Bob",   age=25, subscription_start=date(2023, 1, 1))

    for user in (alice, bob):
        platform.add_user(user)


    return platform

    # another premium user
    carol = PremiumUser("u5", "Carol", age=28, subscription_start=date(2023, 6, 1))

    # family account
    parent = FamilyAccountUser("u3", "Parent", age=40)
    child = FamilyMember("u4", "Child", age=16, parent=parent)

    platform.add_user(carol)
    platform.add_user(parent)
    platform.add_user(child)

    parent.add_sub_user(child)
    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------
    s1 = ListeningSession("s1", bob, t1, RECENT, 180)
    s2 = ListeningSession("s2", alice, t2, RECENT, 210)
    s3 = ListeningSession("s3", bob, t3, RECENT, 195)


    s4 = ListeningSession("s4", bob, t1, RECENT, 180)


    s5 = ListeningSession("s5", alice, t3, RECENT, 195)
    s6 = ListeningSession("s6", bob, t2, RECENT, 210)

    s7 = ListeningSession("s7", alice, t1, OLD, 180)
    s8 = ListeningSession("s8", bob, t3, OLD, 195)

    s9 = ListeningSession("s9", carol, t2, RECENT, 210)
    s10 = ListeningSession("s10", child, t1, RECENT, 180)

    for session in (s1, s2, s3, s4, s5, s6, s7, s8, s9, s10):
        platform.record_session(session)
        session.user.add_session(session)

    # ------------------------------------------------------------------
    # Playlists
    # ------------------------------------------------------------------
    p1 = Playlist("p1", "Alice Mix", owner=alice)
    p1.add_track(t1)
    p1.add_track(t2)
    platform.add_playlist(p1)

    p2 = CollaborativePlaylist("p2", "Shared Mix", owner=bob)
    p2.add_track(t1)
    p2.add_track(t3)
    p2.add_contributor(alice)
    platform.add_playlist(p2)

    p3 = Playlist("p3", "Bob Favorites", owner=bob)
    p3.add_track(t2)
    p3.add_track(t3)
    platform.add_playlist(p3)

    echo = Artist("a2", "Echo", genre="rock")
    platform.add_artist(echo)

    t4 = AlbumTrack("t4", "Stone Echo", 200, "rock", echo, track_number=1)
    platform.add_track(t4)
    echo.add_track(t4)

    p2.add_track(t4)

@pytest.fixture
def fixed_now() -> datetime:
    """Expose the shared FIXED_NOW constant to tests."""
    return FIXED_NOW


@pytest.fixture
def recent_ts() -> datetime:
    return RECENT


@pytest.fixture
def old_ts() -> datetime:
    return OLD
