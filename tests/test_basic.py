import pytest
import sys
sys.path.append('../clementine_last_export/')

from server_management import get_tracks
from server_management import parse_line

#Test functions to be run with pytest                                            
def test_parse_line():                                                           
    assert parse_line("text\tJohn Doe\tTrack 1\ttext") == ("John Doe", "Track 1")
                                                                                 
def test_get_tracks():                                                           
    print((get_tracks("last.fm", "davidsmind")))                                 
    assert (page, totalpages, tracks) == get_tracks("last.fm", "davidsmind")     
