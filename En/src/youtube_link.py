'`Youtube link manager module.'
from .exceptions import *
from .util import is_playlist, is_video, print_exc, with_internet
from pytube import extract, request, Playlist

ERRORS:dict[str, type[Exception]] = {
    'NO_PLAYLIST':PlaylistUnavailable, 'INVALID_URL':InvalidURL, 
    'UNPLAYABLE':VideoUnavailable, 'ERROR':VideoUnavailable,
    'LIVE_STREAM':LiveStreamError,
}

class YouTubeLink:
    '`Link checker class.'
    def __init__(sf) -> None:
        sf.status:str = None
        sf.message:str = None
    
    def start(sf, url:str) -> None:
        '`Stores the url'
        sf.status = None
        sf.url:str = url

    @property
    def is_video(sf) -> bool:
        return is_video(sf.url)
    
    @property
    def is_playlist(sf) -> bool:
        return is_playlist(sf.url)
    
    @property
    def is_available(sf) -> bool:
        '`Check the url status.'
        try: sf.test_url()
        except InternetError:
            sf.message = f'Internet connection lost.'    
        except InvalidURL:
            sf.message = f'Provided an invalid url "{sf.url}".'
        except LiveStreamError:
            sf.message = 'Video is streaming live and cannot be loaded.'
        except VideoUnavailable:
            sf.message = 'Video is unavailable for download, possible reasons: members only, private.'
        except PlaylistUnavailable:
            sf.message = 'Playlist is unavailable.'
        else: return True
        
    @property
    def check_availability(sf) -> None:
        '`Checks the video status.'
        watch_url:str = f'https://youtube.com/watch?v={extract.video_id(sf.url)}'
        sf.status = extract.playability_status(request.get(watch_url))[0]
    
    @with_internet
    def test_url(sf) -> None:
        '`Tests the url.'
        try:
            if not (sf.is_video or sf.is_playlist): sf.status = 'INVALID_URL'
            elif sf.is_video: sf.check_availability
            elif sf.is_playlist and not Playlist(sf.url): sf.status = 'NO_PLAYLIST'
        except Exception:
            print_exc()
            raise InternetError
        if sf.status in ERRORS: raise ERRORS[sf.status]