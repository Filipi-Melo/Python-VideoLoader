'`URLs and downloads manager module.'
from .util import regex_search,with_internet
from .youtube_link import YouTubeLink
from .downloader import Downloader
from .printer import Message
from .exceptions import *
from pytube import YouTube, Playlist
from datetime import timedelta as td
from pathlib import Path

class Manager:
    '`Downloads manager class.'
    def __init__(self,args:dict) -> None:
        self.args = args 
        if self.invalid_args: return
        try:
            
            if self.args["info"]: return self.complete_info(self.args["url"])
            link = Downloader(self.args)
            try:
                if self.args["thumbnail"] and not self.args["playlist"]: link.download_thumbnail(self.args["url"])
                if self.args["audio"] and not self.args["playlist"]: link.download_audio(self.args["url"]) 
                if self.args["video"]: link.download_video(self.args["url"], self.args["resolution"])

            except NoResolutionDesired: Message("The video does not have the selected resolution.","error")
            except LiveStreamError: Message("""Video is streaming live and cannot be loaded.
                      Try again later.""","error")
            
            if self.args["playlist"]: link.download_play_list(self.args["url"], self.args["audio"],
            self.args["thumbnail"], self.args["resolution"])

        except KeyboardInterrupt: Message('Keyboard interrupt.','error')
        except BaseException as exc: Message(f"URL unavailable, error cause:\n{exc}","error")
    
    @property
    def invalid_args(self) -> Message:
        'Checks the arguments.'
        empty:bool = True if True not in [self.args[i] for i in \
        ['video','playlist','audio','thumbnail','info']] else False

        if empty: return Message('Select a button.','error')

        link = YouTubeLink(self.args["url"])
        status = link.available_for_download
        if not status["available"]:
            return Message(status["error_message"],"error")
        
        if self.args["playlist"] and not link.is_playlist: 
            return Message("Playlist flag provided, but it's video url.","error")
        
        if self.args["resolution"] and not regex_search(r"^[\d]{3,4}[p]$",self.args["resolution"]): 
            return Message(f'Provided invalid resolution "{self.args["resolution"]}".',"error")
        
        if not Path.is_dir(self.args["path"]):
            return Message(f'Provided invalid path "{self.args["path"]}".',"error")
                
    @with_internet
    def complete_info(sf, url: str) -> None:
        if sf.args["playlist"]: return sf.show_playlist_info(url)
        sf.show_video_info(url)
    
    def show_video_info(sf, url: str) -> None:
        '`Search and show video information.'
        video = YouTube(url)
        resolutions = sf.available_resolutions(url)
        info = f"""
Video info:
Title: {video.title}
Channel: {video.author}
Views: {video.views}
Duration: {str(td(seconds=video.length))}
Progressive: {" ".join(resolutions["progressive"])}
Adaptive: {" ".join(resolutions["adaptive"])}
Audio: {" ".join(resolutions["audio"])}"""
        Message(info)

    def show_playlist_info(sf, url: str) -> None:
        '`Search and show playlist information.'
        playlist = Playlist(url)
        try:channel="\nChannel: "+playlist.owner
        except:channel=""
        info = f"""
Playlist info:
Title: {playlist.title}{channel}
Views: {playlist.views}
Videos: {playlist.length}"""
        Message(info)
        
    @with_internet
    def available_resolutions(sf, url: str) -> dict:
        '`Returns the available resolutions.'
        video = YouTube(url)
        progressive = video.streams.filter(progressive=True, file_extension='mp4').desc()
        adaptive = video.streams.filter(only_video=True,adaptive=True, file_extension='mp4').desc()
        audio = video.streams.filter(only_audio=True, file_extension='mp4').desc()

        progressive_resolution = [stream.resolution for stream in progressive if stream.resolution]
        adaptive_resolution = [stream.resolution for stream in adaptive if stream.resolution]
        audio_resolution = [stream.abr for stream in audio if stream.abr]
        
        return {"progressive":list(dict.fromkeys(progressive_resolution)),
                "adaptive":list(dict.fromkeys(adaptive_resolution)),
                "audio":list(dict.fromkeys(audio_resolution))}