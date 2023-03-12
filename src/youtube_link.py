'`Youtube link manager module.'
from .exceptions import *
from .util import regex_search
from pytube import extract,request,Playlist

class YouTubeLink:
    '`Link checker class.'
    def __init__(sf, url: str) -> None:
        sf.url, sf.status = url, None

    @property
    def check_video_availability(sf):
        '`Checks the video status.'
        video_id = extract.video_id(sf.url)
        watch_url = f"https://youtube.com/watch?v={video_id}"
        sf.status = extract.playability_status(request.get(url=watch_url))[0]
    
    @property
    def is_video(sf) -> bool:
        return regex_search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", sf.url)

    @property
    def is_playlist(sf) -> bool:
        return regex_search(r"(?:list=)([0-9A-Za-z_-]{11}).*", sf.url)

    @property
    def test_url(sf) -> None:
        '`Tests the url.'
        if not (sf.is_video or sf.is_playlist): raise InvalidURL
        try:
            if sf.is_video: sf.check_video_availability
            if sf.is_playlist and not Playlist(sf.url).videos: sf.status = 'NO_PLAYLIST'
        except: raise InternetError
        
        errors = {'NO_PLAYLIST':PlaylistUnavailable,'UNPLAYABLE':VideoUnavailable,'LIVE_STREAM':LiveStreamError}
        if sf.status in errors: raise errors[sf.status] 

    @property
    def available_for_download(sf) -> dict:
        '`Check the url status.'
        available_flag:bool = True
        error_message:str = None

        try: sf.test_url
        except InternetError:
            available_flag = False
            error_message = f'Internet connection lost.'    
        except InvalidURL:
            available_flag = False
            error_message = f'Provided an invalid url "{sf.url}".'
        except LiveStreamError:
            available_flag = False
            error_message = 'Video is streaming live and cannot be loaded.'
        except VideoUnavailable:
            available_flag = False
            error_message = 'Video is unavailable for download, possible reasons(MembersOnly,Private).'
        except PlaylistUnavailable:
            available_flag = False
            error_message = 'Playlist is unavailable.'
        return {"available": available_flag,"error_message": error_message}