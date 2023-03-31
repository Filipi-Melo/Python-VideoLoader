'`URLs and downloads manager module.'
from .exceptions import NoResolutionDesired, LiveStreamError
from .util import regex_search, with_internet, Urlformat
from .youtube_link import YouTubeLink
from .downloader import Downloader
from .printer import Message
from datetime import timedelta as td
from pytube import YouTube, Playlist
from pathlib import Path

class Manager:
    '`Downloads manager class.'
    def __init__(sf, args:dict[str]) -> None:
        sf.args = args
        sf.args["path"] = Path(sf.args["path"]) if sf.args["path"] else Path.cwd()
        sf.args["url"] = Urlformat(sf.args["url"], sf.args["video"], sf.args["playlist"])

        if sf.invalid_args: return
        try:
            if sf.args["info"]: return sf.complete_info
            link = Downloader(sf.args)
            try:
                if sf.args["thumbnail"] and not sf.args["playlist"]: link.download_thumbnail(sf.args["url"])
                if sf.args["audio"] and not sf.args["playlist"]: link.download_audio(sf.args["url"]) 
                if sf.args["video"]: link.download_video(sf.args["url"], sf.args["resolution"])
            except NoResolutionDesired: Message("The video does not have the selected resolution.","error")
            except LiveStreamError: Message("""Video is streaming live and cannot be loaded.
                      Try again later.""","error")
        
            if sf.args["playlist"]: link.download_play_list(sf.args["url"], sf.args["audio"],
               sf.args["thumbnail"], sf.args["resolution"])
        except KeyboardInterrupt: Message('Keyboard interrupt.','error')
        except Exception as exc: Message(f"URL unavailable, error cause:\n{exc}","error")
    
    @property
    def invalid_args(sf) -> Message:
        '`Checks the arguments.'
        if not len([*filter(lambda i: sf.args[i], ['video','playlist','audio','thumbnail','info'])]): 
            return Message('Select a button.','error')
        
        link = YouTubeLink(sf.args["url"])
        status = link.available_for_download
        if not status["available"]:
            return Message(status["error_message"],"error")
        
        if sf.args["playlist"] and not link.is_playlist: 
            return Message("Playlist flag provided, but it's video url.","error")
        
        if sf.args["resolution"] and not regex_search(r"^[\d]{3,4}[p]$",sf.args["resolution"]): 
            return Message(f'Provided invalid resolution "{sf.args["resolution"]}".',"error")
        
        if not Path.is_dir(sf.args["path"]):
            return Message(f'Provided invalid path "{sf.args["path"]}".',"error")
    
    @property
    @with_internet
    def complete_info(sf) -> None:
        if sf.args["playlist"]: return sf.show_playlist_info(sf.args['url'])
        sf.show_video_info(sf.args['url'])

    @staticmethod
    def show_video_info(url: str) -> None:
        '`Search and shows video information.'
        video = YouTube(url)
        progressive = video.streams.filter(progressive=True, file_extension='mp4').desc()
        adaptive = video.streams.filter(only_video=True,adaptive=True, file_extension='mp4').asc()
        audio = video.streams.filter(only_audio=True, file_extension='mp4').desc()
    
        Message( f"""
Video info:
Title: {video.title}.
Channel: {video.author}.
Views: {video.views:,}.
Duration: {str(td(seconds=video.length))}.
Progressive: {", ".join({}.fromkeys( map(lambda stream: stream.resolution, progressive)))}.
Adaptive: {", ".join({}.fromkeys( map(lambda stream: stream.resolution, adaptive)))}.
Audio: {", ".join({}.fromkeys( map(lambda stream: stream.abr, audio)))}.""" )

    @staticmethod
    def show_playlist_info(url: str) -> None:
        '`Search and shows playlist information.'
        playlist = Playlist(url)
        try: channel = f"\nChannel: {playlist.owner}."
        except: channel = ""

        Message( f"""
Playlist info:
Title: {playlist.title}.{channel}
Views: {playlist.views:,}.
Videos: {playlist.length}.""" )