'`Video and playlist downloader module.'
from .exceptions import NoResolutionDesired, LiveStreamError
from .util import with_internet, download_image
from .printer import Message, show, colored
from .youtube_link import YouTubeLink
from .load_bar import LoadBar
from pytube import YouTube, Playlist
from datetime import timedelta as td
from pathlib import Path

class Downloader:
    '`Class downloader of videos, audios, thumbs and playlists.'
    def __init__(self,args: dict) -> None:
        self.args=args
        self.video_prefix = "Py VLoader video_"
        self.audio_prefix = "Py VLoader audio_"
        
    @with_internet
    def download_thumbnail(self, url: str) -> None:
        '`Download the thumbnail.'
        link = YouTubeLink(url)
        if not link.is_video and link.is_playlist : return  
    
        video = YouTube(url)    
        self.show_info(video)
        info = f"""
Video information:
Title: {video.title}
Channel: {video.author}
Duration: {str(td(seconds=video.length))}

Thumbnail downloaded successfully!"""
        status='success'

        try: download_image(
            url=video.thumbnail_url,
            name=video.title,
            output_folder=self.args["path"])
        except BaseException as exc:
            info,status = f'Unable to download thumbnail.\nError cause: {exc}','error'
            if self.args["playlist"]: return show(info+"\n",status)

        if not (self.args["playlist"] or self.args["video"]):
            Message(info,status)

    def download_audio(self, url: str):
        '`Download the audio.'
        link = YouTubeLink(url)
        if not link.is_video and link.is_playlist: return  
        
        Bar=LoadBar()
        video = YouTube(url,
            on_progress_callback= lambda stream,fh,bytes: Bar.update(bytes),
            on_complete_callback= lambda a,b: show("\nDownloaded successfully!\n"))
        
        self.show_info(video) 
        stream = video.streams.filter(only_audio=True, file_extension='mp4').desc().first()
        if not stream: raise LiveStreamError
        
        show("Downloading the audio:")
        Bar.total_size = stream.filesize
        Bar.update(stream.filesize)
        file = stream.download(
            output_path=self.args["path"],
            filename_prefix=self.audio_prefix)
        
        path = Path(file)
        try: path.rename(path.with_suffix('.mp3'))
        except FileExistsError:
            path.unlink()
            return show("File already exists!\n","error")
            
        if not (self.args["playlist"] or self.args["video"]): 
            Message(self.info(video, Bar.filesize),"success")
    
    @with_internet
    def download_video(self,url:str,resolution:str) -> None:
        '`Download the video.'
        link = YouTubeLink(url)
        if link.is_playlist and not link.is_video: return
        if resolution and not self.args['audio']: self.download_audio(url)
        
        Bar = LoadBar()
        video = YouTube(url,
            on_progress_callback= lambda stream,fh, bytes: Bar.update(bytes),
            on_complete_callback= lambda a,b: show("\nDownloaded successfully!\n"))
        
        if not (self.args['thumbnail'] or resolution): self.show_info(video)
        
        stream = video.streams.get_highest_resolution()\
        if not resolution else self.get_resolution(video.streams, resolution)
        if not stream: raise LiveStreamError
        
        show("Downloading the video:")
        Bar.total_size = stream.filesize
        Bar.update(stream.filesize)
        stream.download(
            output_path=self.args["path"],
            filename_prefix=self.video_prefix)
        if not self.args["playlist"]:
            Message(self.info(video, Bar.filesize),"success")

    def info(self,video:YouTube, size:str) -> str:
        '`Returns the downloaded video information.'
        return f"""
Video information:
Title: {video.title}
Channel: {video.author}
Duration: {str(td(seconds=video.length))}
Size: {size}

|{size}| {'█'*18} 100% 

Downloaded successfully!"""
        
    @with_internet
    def download_play_list(self, url: str, audio_flag: bool, thumbnail_flag: bool, resolution: str) -> None:
        '`Downloads the Playlist.'
        success:bool=True
        for video in Playlist(url).videos:
            try:
                status = YouTubeLink(video.watch_url).available_for_download
                if not status["available"]:
                    success,_ = show(status["error_message"],"error"),show("Video skipped.\n","warning")
                    continue
                if thumbnail_flag: self.download_thumbnail(video.watch_url)
                if audio_flag: self.download_audio(video.watch_url)
                if not (audio_flag or thumbnail_flag): self.download_video(video.watch_url, resolution)

            except NoResolutionDesired:
                show("The video does not have the selected resolution.","error")
                success = show("Video skipped.\n","warning")
            except LiveStreamError: 
                success = show('\nVideo is streaming live and cannot be loaded.\n'+
                'Try again later.\n',"error")
            except KeyboardInterrupt:
                success = show('Keyboard interrupt.\n','error')
            except BaseException as exc: success = show(f"\nVideo unavailable, error cause:\n{exc}","error")

        text,type = ('Playlist downloaded successfully!','success')\
        if success else ('Unable to download playlist successfully.','error')
        Message(text,type)

    def get_resolution(self, streams: YouTube.streams, resolution: str):
        '`Get available resolutions.'
        for stream in streams.filter(adaptive=True,file_extension='mp4').desc():
            if stream.resolution == resolution: return stream
        raise NoResolutionDesired

    def show_info(self, video: YouTube) -> None:
        '`Shows the video information.'
        print(f"""{colored("Video information:","warning")}
{colored("Title:")} {video.title}
{colored("Channel:")} {video.author}
{colored("Duration:")} {str(td(seconds=video.length))}\n""")