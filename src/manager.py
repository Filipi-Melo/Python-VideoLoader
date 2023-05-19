'`URLs and downloads manager module.'
from .exceptions import NoResolutionDesired, LiveStreamError
from .util import regex_search, with_internet, Urlformat
from .youtube_link import YouTubeLink
from .downloader import Downloader
from .printer import Message
from datetime import timedelta as td
from pytube import YouTube, Playlist, StreamQuery
from pathlib import Path

class Manager:
    '`Downloads manager class.'
    def __init__(sf, args:dict) -> None:
        sf.args:dict = args
        sf.args["path"] = Path(sf.args["path"]) if sf.args["path"] else Path.cwd()
        sf.args["url"] = Urlformat(sf.args["url"].strip(), sf.args["playlist"])

        if sf.invalid_args: return
        try:
            if sf.args["info"]: return sf.complete_info
            link:Downloader = Downloader(sf.args)
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
    def invalid_args(sf) -> Message|None:
        '`Checks the arguments.'
        if not any(filter(lambda k: sf.args[k], ('video','playlist','audio','thumbnail','info'))):
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
        if sf.args["playlist"]: return show_playlist_info(sf.args['url'])
        show_video_info(sf.args['url'])

def show_video_info(url:str) -> None:
    '`Search and shows video information.'
    video:YouTube = YouTube(url)
    progressive:StreamQuery = video.streams.filter(progressive=True, file_extension='mp4')
    adaptive:StreamQuery = video.streams.filter(only_video=True,adaptive=True, file_extension='mp4')
    audio:StreamQuery = video.streams.filter(only_audio=True, file_extension='mp4')
    
    def key(Str:str) -> int: return int(Str.replace('kbps','').replace('p',''))

    Message(f"""
Video info:
Title: {video.title}.
Channel: {video.author}.
Views: {video.views:,}.
Duration: {str(td(seconds=video.length))}.
Progressive: {", ".join(sorted(set(stream.resolution for stream in progressive), key=key))}.
Adaptive: {", ".join(sorted(set(stream.resolution for stream in adaptive), key=key))}.
Audio: {", ".join(sorted(set(stream.abr for stream in audio), key=key))}.""")

def show_playlist_info(url:str) -> None:
    '`Search and shows playlist information.'
    playlist:Playlist = Playlist(url)
    try: channel:str = f"\nCanal: {playlist.owner}."
    except: channel:str = ""

    Message(f"""
Playlist info:
Title: {playlist.title}.{channel}
Views: {playlist.views:,}.
Videos: {playlist.length}.""")