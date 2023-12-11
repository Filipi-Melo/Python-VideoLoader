'`Módulo gerenciador de urls e downloads.'
from .exceptions import NoResolutionDesired, LiveStreamError, HTTPError
from .util import dateform, formatURL, is_res, length, print_exc, with_internet
from .youtube_link import YouTubeLink
from .downloader import Downloader
from .printer import Message
from pytube import YouTube, Playlist, StreamQuery
from pathlib import Path
from typing import Callable, Iterable

class Manager:
    '`Classe gerenciadora de downloads.'
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
            except NoResolutionDesired: error('O vídeo não tem a resolução selecionada.')
            except LiveStreamError: error('O vídeo é uma estreia e não pôde ser baixado.\nTente novamente mais tarde.')
            except HTTPError as exc: 
                if exc.code == 403: return error(f'"{sf.url}"\nO acesso ao vídeo foi negado.\nTente novamente mais tarde')
                error(f'{exc}.\nO vídeo não pôde ser baixado.\nTente novamente mais tarde')
        except KeyboardInterrupt: error('Interrompido pelo teclado.')
        except Exception as exc:
            print_exc()
            error(f'URL indisponível:\n"{sf.url}"\nCausa do erro:\n{exc}')
    
    @property
    def valid_args(sf) -> bool:
        '`Verifica os argumentos.'
        if not any([sf.video, sf.pl, sf.audio, sf.thumb, sf.info]): return error('Selecione um botão.')

        sf.link.start(sf.url)
        if sf.video and not sf.link.is_video: 
            return error(f'Foi providenciada uma url inválida:\n"{sf.url}".')

        if sf.pl and not sf.link.is_playlist: 
            return error('Sinalizador de playlist fornecido, mas é a url de vídeo.')

        if sf.resolution and not is_res(sf.resolution): 
            return error(f'Foi providenciada uma resolução inválida:\n"{sf.resolution}".')

        if not sf.path.is_dir(): 
            return error(f'Foi providenciado um diretório inválido:\n"{sf.path}".')

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
        '`Pesquisa as informações do vídeo.`'
        video:YouTube = YouTube(url)
        streams:StreamQuery = video.streams

        progressive:StreamQuery = streams.filter(progressive=True, file_extension='mp4')
        adaptive:StreamQuery = streams.filter(only_video=True, adaptive=True, file_extension='mp4')
        audio:StreamQuery = streams.filter(only_audio=True, file_extension='mp4')
        
        return f'''Informação do video:
Titulo: {video.title}.
Canal: {video.author}.
Visualizações: {video.views:,}.
Publicação: {dateform(video.publish_date)}.
Duração: {length(video.length)}.
Progressivo: {join(stream.resolution for stream in progressive)}.
Adaptável: {join(stream.resolution for stream in adaptive)}.
Audio: {join(stream.abr for stream in audio)}.'''

    @staticmethod
    def playlist_info(url:str) -> str:
        '`Pesquisa as informações da playlist.'
        playlist:Playlist = Playlist(url)
        
        try: channel:str = f'\nCanal: {playlist.owner}.'
        except KeyError: channel = ''

        return f'''Informação da playlist:
Titulo: {playlist.title}.{channel}
Atualizada: {dateform(playlist.last_updated)}.
Visualizações: {playlist.views:,}.
Videos: {playlist.length}.'''

def error(message:str) -> None:
    '`Mostra os erros.'
    Message(message.splitlines(), 'error')

def join(it:Iterable[str]) -> str: 
    '`Organiza as resoluções do vídeo.'
    return ', '.join(sorted(set(it), key=lambda s: int(s.removesuffix('kbps').removesuffix('p'))))