'`URLs and downloads manager module.'
from .exceptions import NoResolutionDesired, LiveStreamError, HTTPError
from .util import dateform, formatURL, is_res, length, print_exc, with_internet
from .youtube_link import YouTubeLink
from .downloader import Downloader
from .printer import Message
from pytube import YouTube, Playlist, StreamQuery
from pathlib import Path
from typing import Callable, Iterable

class Manager:
    '`Download manager class.'
    cwd:Path = Path.cwd()
    infocache:dict[str,dict[str,str]] = {'pl':{}, 'vid':{}}
    downloader:Downloader = Downloader()
    link:YouTubeLink = YouTubeLink()

    def __init__(sf, args:dict[str, str|bool]) -> None:
        sf.audio:bool = args['audio']
        sf.video:bool = args['video']
        sf.pl:bool = args['playlist']
        sf.thumb:bool = args['thumbnail']
        sf.info:bool = args['info']
        sf.path:Path = Path(args['path'].strip() or sf.cwd)
        sf.resolution:str = args['resolution']
        sf.url:str = formatURL(args['url'].strip())

        if not sf.valid_args: return
        try:
            if sf.info: return sf.getinfo('vid' if not sf.pl else 'pl')
            sf.downloader.start(sf.audio, sf.thumb, sf.path, sf.resolution)

            if sf.pl: return sf.downloader.download_playlist(sf.url)
            try:
                if sf.audio: sf.downloader.download_audio(sf.url)
                elif sf.thumb: sf.downloader.download_thumbnail(sf.url)
                else: sf.downloader.download_video(sf.url)
            except NoResolutionDesired: error('The video does not have the selected resolution.')
            except LiveStreamError: error('Video is streaming live and cannot be loaded.\nTry again later.')
            except HTTPError as exc: 
                if exc.code == 403: return error(f'"{sf.url}"\nAccess to the video was denied.\nTry again later.')
                error(f'{exc}.\nThe video cannot be loaded.\nTry again later.')
        except KeyboardInterrupt: error('Keyboard interrupt.')
        except Exception as exc:
            print_exc()
            error(f'URL unavailable:\n"{sf.url}"\nError cause:\n{exc}')

    @property
    def valid_args(sf) -> bool:
        '`Checks the arguments.'
        if not any([sf.video, sf.pl, sf.audio, sf.thumb, sf.info]): return error('Select a button.')

        sf.link.start(sf.url)
        if sf.video and not sf.link.is_video: 
            return error(f'Provided an invalid url:\n"{sf.url}".')

        if sf.pl and not sf.link.is_playlist: 
            return error('Playlist flag provided, but it\'s video url.')

        if sf.resolution and not is_res(sf.resolution): 
            return error(f'Provided an invalid resolution:\n"{sf.resolution}".')

        if not sf.path.is_dir(): 
            return error(f'Provided an invalid path:\n"{sf.path}".')

        if not sf.link.is_available: return error(sf.link.message)
        return True
    
    @with_internet
    def getinfo(sf, key:str) -> None:
        options:dict[str,Callable[[str],str]] = {'pl':sf.playlist_info, 'vid':sf.video_info}

        if not sf.url in sf.infocache[key]: 
            sf.infocache[key].update({sf.url:options[key](sf.url)})
        Message(sf.infocache[key][sf.url].split('\n', 1))

    @staticmethod
    def video_info(url:str) -> str:
        '`Search video information.'
        video:YouTube = YouTube(url)
        streams:StreamQuery = video.streams

        progressive:StreamQuery = streams.filter(progressive=True, file_extension='mp4')
        adaptive:StreamQuery = streams.filter(only_video=True, adaptive=True, file_extension='mp4')
        audio:StreamQuery = streams.filter(only_audio=True, file_extension='mp4')

        return f'''Video info:
Title: {video.title}.
Channel: {video.author}.
Views: {video.views:,}.
Publication: {dateform(video.publish_date)}.
Duration: {length(video.length)}.
Progressive: {join(stream.resolution for stream in progressive)}.
Adaptive: {join(stream.resolution for stream in adaptive)}.
Audio: {join(stream.abr for stream in audio)}.'''

    @staticmethod
    def playlist_info(url:str) -> str:
        '`Search playlist information.'
        playlist:Playlist = Playlist(url)
        
        try: channel:str = f'\nChannel: {playlist.owner}.'
        except KeyError: channel = ''

        return f'''Playlist info:
Title: {playlist.title}.{channel}
Updated: {dateform(playlist.last_updated)}.
Views: {playlist.views:,}.
Videos: {playlist.length}.'''

def error(message:str) -> None:
    '`Shows errors.'
    Message(message.splitlines(), 'error')

def join(it:Iterable[str]) -> str: 
    '`Arranges video resolutions.'
    return ', '.join(sorted(set(it), key=lambda s: int(s.removesuffix('kbps').removesuffix('p'))))