'`Youtube link manager module.'
from .exceptions import *
from .util import regex_search
from pytube import extract,request,Playlist

class YouTubeLink:
    '`Link checker class.'
    def __init__(self, url: str) -> None:
        self.url = url
        self.status=None

    @property
    def check_video_availability(self):
        '`Checks the video status.'
        video_id = extract.video_id(self.url)
        watch_url = f"https://youtube.com/watch?v={video_id}"
        self.status, _ = extract.playability_status(request.get(url=watch_url))
    
    @property
    def is_video(self) -> bool:
        return regex_search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", self.url)

    @property
    def is_playlist(self) -> bool:
        return regex_search(r"(?:list=)([0-9A-Za-z_-]{11}).*", self.url)

    @property
    def test_url(self) -> None:
        '`Tests the url.'
        if not (self.is_video or self.is_playlist): raise InvalidURL
        try:
            if self.is_video: self.check_video_availability
            if self.is_playlist and not Playlist(self.url).videos: self.status='NO_PLAYLIST'
        except: raise InternetError
        
        if self.status=='NO_PLAYLIST': raise PlaylistUnavailable 
        if self.status == 'UNPLAYABLE': raise VideoUnavailable
        if self.status == 'LIVE_STREAM': raise LiveStreamError
        
    @property
    def available_for_download(self) -> dict:
        '`Check the url status.'
        available_flag:bool = True
        error_message:str = None

        try: self.test_url
        except InternetError:
            available_flag = False
            error_message = f'Internet connection lost.'    
        except InvalidURL:
            available_flag = False
            error_message = f'Provided an invalid url "{self.url}".'
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