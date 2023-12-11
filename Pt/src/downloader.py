'`Módulo baixador de vídeos e playlists.'
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
    '`Classe baixadora de vídeos, audios, thumbs e playlists.'
    video_prefix:str = 'Py VLoader video_'
    audio_prefix:str = 'Py VLoader audio_'
    link:YouTubeLink = YouTubeLink()
    bar:LoadBar = LoadBar()

    def start(sf, audio:bool, thumb:bool, path:Path, resolution:str) -> None:
        '`Inicia as variáveis da instância.'
        sf.audio:bool = audio
        sf.thumb:bool = thumb
        sf.path:Path = path
        sf.resolution:str = resolution
    
    @with_internet
    def download_thumbnail(sf, url:str) -> None:
        '`Baixa a thumbnail do vídeo.'
        video:YouTube = YouTube(url)
        show_info(video)
        
        text:str = f'''Informação do vídeo:
Titulo: {video.title}
Canal: {video.author}
Visualizações: {video.views:,}
Duração: {length(video.length)}
Thumbnail baixada com sucesso!'''

        try: download_image(
                video.thumbnail_url,
                safe_filename(video.title),
                sf.path
            )
        except Exception as exc:
            print_exc()
            text = f'Não foi possível baixar a Thumbnail.\nCausa do erro:\n{exc}.'
            Message(text.splitlines(), 'error')
            return show(text + '\n', 'error')
        
        Message(text, 'success', 1)
    
    def getfile(sf, stream:Stream, prefix:str, suffix:str) -> str:
        '`Obtém o nome do arquivo.'
        name:str = stream.get_file_path(
            output_path=sf.path,
            filename_prefix=prefix
        ).rsplit('.', 1)[0]

        if not Path(name + suffix).exists(): return name + '.mp4'

        for n in count(1):
            if not Path(f'{name}({n}){suffix}').exists(): 
                return f'{name}({n}).mp4'

    def download(sf, url:str, prefix:str, audio:bool=False, info:bool=True) -> tuple[Path, YouTube]:
        '`Baixa o video ou audio.'
        video:YouTube = YouTube(url,
            on_progress_callback = sf.bar.onprogress,
            on_complete_callback = sf.bar.oncomplete
        )
        if info: show_info(video)

        if audio: stream:Stream = video.streams.get_audio_only()
        elif sf.resolution: stream:Stream = get_resolution(video.streams, sf.resolution) 
        else: stream:Stream = video.streams.get_highest_resolution()
        if not stream: raise LiveStreamError

        show('Baixando o audio:' if audio else 'Baixando o vídeo:')
        sf.bar.start(stream.filesize)

        return Path(stream.download(filename=sf.getfile(
            stream, prefix, '.mp3' if audio else '.mp4'))), video

    @with_internet
    def download_audio(sf, url:str) -> None:
        '`Baixa o audio.'
        file, video = sf.download(url, sf.audio_prefix, True)
        
        print(colored('Processando audio...', 'warning'), end='\r')
        unifyclips(None, file, file)
        file.rename(file.with_suffix('.mp3'))

        Message(info(video, sf.bar.size), 'success', 2)

    @with_internet
    def download_video(sf, url:str) -> None:
        '`Baixa o vídeo.'
        file, video = sf.download(url, sf.video_prefix)
        size:str = sf.bar.size

        if sf.resolution:
            temp:Path = file.with_stem(file.stem + '_temp')
            audio:Path = sf.download(url, sf.audio_prefix, True, False)[0]
        
            print(colored('Processando video...', 'warning'), end='\r')
            unifyclips(file, audio, temp)
            audio.unlink()
            temp.replace(file)

        Message(info(video, size), 'success', 2)

    @with_internet
    def download_playlist(sf, playlist:str) -> None:
        '`Baixa a Playlist.'
        status:bool = True
        for video in Playlist(playlist).videos:
            try:
                url:str = video.watch_url
                sf.link.start(url)

                if not sf.link.is_available:
                    status = error(video, sf.link.message)
                    show('Vídeo pulado.\n', 'warning')
                    continue
                
                if sf.audio: sf.download_audio(url)
                elif sf.thumb: sf.download_thumbnail(url)
                else: sf.download_video(url)
            except NoResolutionDesired:
                status = error(video, 'O vídeo não tem a resolução selecionada.')
                show('Vídeo pulado.\n', 'warning')
            except LiveStreamError:
                status = error(video, 'O vídeo é uma estreia e não pôde ser baixado.\nTente novamente mais tarde.')
            except KeyboardInterrupt:
                status = error(video, 'Interrompido pelo teclado.')
            except HTTPError as exc:
                status = error(video, f'"{url}"\nO acesso ao vídeo foi negado.\nTente novamente mais tarde.' if exc.code == 403
                                else f'{exc}.\nO vídeo não pôde ser baixado.\nTente novamente mais tarde.')
            except Exception as exc:
                print_exc()
                status = error(video, f'Vídeo indisponível, causa do erro:\n{exc}.')
        
        Message(*('Playlist baixada com sucesso!', 'success') if status else
                 ('Não foi possível baixar com sucesso a playlist.', 'error'))

def info(video:YouTube, size:str) -> str:
    '`Retorna as informações do vídeo baixado.'
    return f'''Informação do vídeo:
Titulo: {video.title}
Canal: {video.author}
Visualizações: {video.views:,}
Duração: {length(video.length)}
Tamanho: {size}
{' ' * 70}
|{size}| [{'█'*20}] 100%
Baixado com sucesso!'''

def get_resolution(streams:StreamQuery, resolution:str) -> Stream:
    '`Obtêm as resoluções disponíveis.'
    stream:Stream = streams.filter(res=resolution, adaptive=True, file_extension='mp4').first()
    if stream: return stream
    raise NoResolutionDesired

def show_info(video:YouTube) -> None:
    '`Mostra as informações do vídeo.' 
    print(f'''{colored('Informação do vídeo:','warning')}
{colored('Titulo:')} {video.title}
{colored('Canal:')} {video.author}
{colored('Visualizações:')} {video.views:,}
{colored('Duração:')} {length(video.length)}\n''')

def error(video:YouTube, message:str) -> None:
    '`Mostra os erros.'
    show(message + '\n', 'error')
    Message(f'{video.title}\n{message}'.splitlines(), 'error')