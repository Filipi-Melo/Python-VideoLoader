'`Video and playlist downloader module.'
from .exceptions import NoResolutionDesired, LiveStreamError
from .util import with_internet, download_image
from .printer import Message, show, colored
from .youtube_link import YouTubeLink
from .load_bar import LoadBar
from datetime import timedelta as td
from pytube import YouTube, Playlist
from pathlib import Path
 
class Downloader:
    '`Class downloader of videos, audios, thumbs and playlists.'
    def __init__(sf,args: dict) -> None:
        sf.args, sf.video_prefix, sf.audio_prefix = (args,"Py VLoader video_","Py VLoader audio_")
        
    @with_internet
    def download_thumbnail(sf, url:str) -> None:
        '`Download the thumbnail.'
        link = YouTubeLink(url)
        if not link.is_video and link.is_playlist: return  

        video = YouTube(url)    
        sf.show_info(video)
        text = [f"""
Video information:
Title: {video.title}
Channel: {video.author}
Duration: {str(td(seconds=video.length))}

Thumbnail downloaded successfully!""", 'success']

        try: download_image(
            video.thumbnail_url,
            ''.join(filter(lambda c: c not in '/|\\?:<>*',video.title)),
            sf.args["path"])
        except Exception as exc:
            text = [f'Unable to download thumbnail.\nError cause: {exc}','error']
            show(text[0]+"\n", text[1])
        Message(*text)

    @with_internet
    def download_audio(sf, url: str) -> None:
        '`Download the audio.'
        link = YouTubeLink(url)
        if not link.is_video and link.is_playlist: return  
        
        Bar = LoadBar()
        video = YouTube(url,
            on_progress_callback= lambda stream,fh,bytes: Bar.update(bytes),
            on_complete_callback= lambda a,b: show("\nDownloaded successfully!\n")
        )
        if not sf.args['thumbnail']: sf.show_info(video)
        stream = video.streams.filter(only_audio=True, file_extension='mp4').desc()[0]
        if not stream: raise LiveStreamError

        show("Downloading the audio:")
        Bar.total = stream.filesize
        Bar.update(stream.filesize)
        file = stream.download(
            output_path=sf.args["path"],
            filename_prefix=sf.audio_prefix
        )
        text = [sf.info(video, Bar.filesize),"success"]
        path = Path(file)
        try: path.rename(path.with_suffix('.mp3'))
        except FileExistsError:
            path.unlink()
            text = ['File already exists!','error']
            show(text[0]+'\n',text[1])  
        Message(*text)

    @with_internet
    def download_video(sf,url:str,resolution:str) -> None:
        '`Download the video.'
        link = YouTubeLink(url)
        if link.is_playlist and not link.is_video: return
        if resolution and not sf.args['audio']: sf.download_audio(url)

        Bar = LoadBar()
        video = YouTube(url,
            on_progress_callback= lambda stream,fh, bytes: Bar.update(bytes),
            on_complete_callback= lambda a,b: show("\nDownloaded successfully!\n")
        )
        if not (sf.args['thumbnail'] or sf.args['audio'] or resolution): sf.show_info(video)
        
        stream = video.streams.get_highest_resolution() if not resolution \
        else sf.get_resolution(video.streams, resolution)
        if not stream: raise LiveStreamError

        show("Downloading the video:")
        Bar.total = stream.filesize
        Bar.update(stream.filesize)
        stream.download(
            output_path=sf.args["path"],
            filename_prefix=sf.video_prefix
        )
        Message(sf.info(video, Bar.filesize),"success")

    @with_internet
    def download_play_list(sf, url: str, audio_flag: bool, thumbnail_flag: bool, resolution: str) -> None:
        '`Downloads the Playlist.'
        success:bool = True
        for video in Playlist(url).videos:
            try:
                status = YouTubeLink(video.watch_url).available_for_download
                if not status["available"]:
                    success = (error(video,status["error_message"]),show("Video skipped.\n","warning"))[0]
                    continue
                if thumbnail_flag: sf.download_thumbnail(video.watch_url)
                if audio_flag: sf.download_audio(video.watch_url)
                if not (audio_flag or thumbnail_flag): sf.download_video(video.watch_url, resolution)
            except NoResolutionDesired:
                success = (error(video,"The video does not have the selected resolution."),
                           show("Video skipped.\n","warning"))[0]
            except LiveStreamError:
                success = error(video, 'Video is streaming live and cannot be loaded.\n'+
                'Try again later.\n')
            except KeyboardInterrupt:
                success = error(video,'Keyboard interrupt.\n')
            except Exception as exc:
                success = error(video, f"Video unavailable, error cause:\n{exc}")
        Message(*( ('Playlist downloaded successfully!','success') if success \
            else ('Unable to download playlist successfully.','error') ))
    
    @staticmethod
    def info(video:YouTube, size:str) -> str:
        '`Returns the downloaded video information.'
        return f"""
Video information:
Title: {video.title}
Channel: {video.author}
Duration: {str(td(seconds=video.length))}
Size: {size}

|{size}| {'???'*20} 100% 

Downloaded successfully!"""

    @staticmethod
    def get_resolution(streams: YouTube.streams, resolution: str):
        '`Get available resolutions.'
        for stream in streams.filter(res=resolution,adaptive=True,file_extension='mp4').desc():
            if stream.resolution == resolution: return stream
        raise NoResolutionDesired

    @staticmethod
    def show_info(video: YouTube) -> None:
        '`Shows the video information.'
        print( f"""{colored("Video information:","warning")}
{colored("Title:")} {video.title}
{colored("Channel:")} {video.author}
{colored("Duration:")} {str(td(seconds=video.length))}\n""" )

def error(video:YouTube, message:str) -> None:
    '`Shows errors.'
    show(message,'error'), Message(video.title+'\n\n'+message,'error')