'`Video and playlist downloader module.'
from .exceptions import NoResolutionDesired, LiveStreamError, HTTPError
from .util import with_internet, download_image, print_exc, length, unifyclips
from .printer import Message, show, colored
from .youtube_link import YouTubeLink
from .load_bar import LoadBar
from itertools import count
from pathlib import Path
from pytube import YouTube, Playlist, StreamQuery, Stream
from pytube.helpers import safe_filename

class Downloader:
    '`Class downloader of videos, audios, thumbs and playlists.'
    video_prefix:str = 'Py VLoader video_'
    audio_prefix:str = 'Py VLoader audio_'
    link:YouTubeLink = YouTubeLink()
    bar:LoadBar = LoadBar()

    def start(sf, audio:bool, thumb:bool, path:Path, resolution:str) -> None:
        '`starts the instance variables.'
        sf.audio:bool = audio
        sf.thumb:bool = thumb
        sf.path:Path = path
        sf.resolution:str = resolution
    
    @with_internet
    def download_thumbnail(sf, url:str) -> None:
        '`Download the thumbnail.'
        video:YouTube = YouTube(url)
        show_info(video)
        
        text:str = f'''Video info:
Title: {video.title}
Channel: {video.author}
views: {video.views:,}
Duration: {length(video.length)}
Thumbnail downloaded successfully!'''
        
        try: download_image(
                video.thumbnail_url,
                safe_filename(video.title),
                sf.path
            )
        except Exception as exc:
            print_exc()
            text = f'Unable to download thumbnail.\nError cause:\n{exc}.'
            Message(text.splitlines(), 'error')
            return show(text + '\n', 'error')
        
        Message(text, 'success', 1)
    
    def getfile(sf, stream:Stream, prefix:str, suffix:str) -> str:
        '`Gets the file name.'
        name:str = stream.get_file_path(
            output_path=sf.path,
            filename_prefix=prefix
        ).rsplit('.', 1)[0]

        if not Path(name + suffix).exists(): return name + '.mp4'

        for n in count(1):
            if not Path(f'{name}({n}){suffix}').exists(): 
                return f'{name}({n}).mp4'

    def download(sf, url:str, prefix:str, audio:bool=False, info:bool=True) -> tuple[Path, YouTube]:
        '`Download the video or audio.'
        video:YouTube = YouTube(url,
            on_progress_callback = sf.bar.onprogress,
            on_complete_callback = sf.bar.oncomplete
        )
        if info: show_info(video)

        if audio: stream:Stream = video.streams.get_audio_only()
        elif sf.resolution: stream:Stream = get_resolution(video.streams, sf.resolution) 
        else: stream:Stream = video.streams.get_highest_resolution()
        if not stream: raise LiveStreamError

        show('Downloading the audio:' if audio else 'Downloading the video:')
        sf.bar.start(stream.filesize)
        
        return Path(stream.download(filename=sf.getfile(
            stream, prefix, '.mp3' if audio else '.mp4'))), video
    
    @with_internet
    def download_audio(sf, url:str) -> None:
        '`Download the audio.'
        file, video = sf.download(url, sf.audio_prefix, True)
        
        print(colored('Processing audio...', 'warning'), end='\r')
        unifyclips(None, file, file)
        file.rename(file.with_suffix('.mp3'))

        Message(info(video, sf.bar.size), 'success', 2)

    @with_internet
    def download_video(sf, url:str) -> None:
        '`Download the video.'
        file, video = sf.download(url, sf.video_prefix)
        size:str = sf.bar.size

        if sf.resolution:
            temp:Path = file.with_stem(file.stem + '_temp')
            audio:Path = sf.download(url, sf.audio_prefix, True, False)[0]
        
            print(colored('Processing video...', 'warning'), end='\r')
            unifyclips(file, audio, temp)
            audio.unlink()
            temp.replace(file)

        Message(info(video, size), 'success', 2)

    @with_internet
    def download_playlist(sf, playlist:str) -> None:
        '`Downloads the Playlist.'
        status:bool = True
        for video in Playlist(playlist).videos:
            try:
                url:str = video.watch_url 
                sf.link.start(url)

                if not sf.link.is_available:
                    status = error(video, sf.link.message)
                    show('Video skipped.\n', 'warning')
                    continue

                if sf.audio: sf.download_audio(url)
                elif sf.thumb: sf.download_thumbnail(url)
                else: sf.download_video(url)
            except NoResolutionDesired:
                status = error(video, 'The video does not have the selected resolution.')
                show('Video skipped.\n', 'warning')
            except LiveStreamError:
                status = error(video, 'Video is streaming live and cannot be loaded.\nTry again later.')
            except KeyboardInterrupt:
                status = error(video, 'Keyboard interrupt.\n')
            except HTTPError as exc: 
                status = error(video, f'"{url}"\nAccess to the video was denied.\nTry again later.' if exc.code == 403
                                else f'{exc}.\nThe video cannot be loaded.\nTry again later.')
            except Exception as exc:
                print_exc()
                status = error(video, f'Video unavailable, error cause:\n{exc}\n')
        
        Message(*('Playlist downloaded successfully!', 'success') if status else
                 ('Unable to download playlist successfully.', 'error'))

def info(video:YouTube, size:str) -> str:
    '`Returns the downloaded video information.'
    return f'''Video information:
Title: {video.title}
Channel: {video.author}
Views: {video.views:,}
Duration: {length(video.length)}
Size: {size}
{' ' * 70}
|{size}| [{'█'*20}] 100%
Downloaded successfully!'''
    
def get_resolution(streams:StreamQuery, resolution:str) -> Stream:
    '`Get available resolutions.'
    stream:Stream = streams.filter(res=resolution, adaptive=True, file_extension='mp4').first()
    if stream: return stream
    raise NoResolutionDesired

def show_info(video:YouTube) -> None:
    '`Shows the video information.'
    print(f'''{colored('Video information:','warning')}
{colored('Title:')} {video.title}
{colored('Channel:')} {video.author}
{colored('Views:')} {video.views:,}
{colored('Duration:')} {length(video.length)}\n''')

def error(video:YouTube, message:str) -> None:
    '`Shows errors.'
    show(message + '\n', 'error')
    Message(f'{video.title}\n{message}'.splitlines(), 'error')