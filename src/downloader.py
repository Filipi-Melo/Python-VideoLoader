'`Módulo baixador de vídeos e playlists.'
from .exceptions import NoResolutionDesired, LiveStreamError
from .util import with_internet, download_image
from .printer import Message, show, colored
from .youtube_link import YouTubeLink
from .load_bar import LoadBar
from datetime import timedelta as td
from pytube import YouTube, Playlist, StreamQuery, Stream
from pathlib import Path

class Downloader:
    '`Classe baixadora de vídeos, audios, thumbs e playlists.'
    def __init__(sf, args:dict) -> None:
        sf.args, sf.video_prefix, sf.audio_prefix = (args, "Py VLoader video_", "Py VLoader audio_")

    @with_internet
    def download_thumbnail(sf, url: str) -> None:
        '`Baixa a thumbnail do vídeo.'
        link:YouTubeLink = YouTubeLink(url)
        if not link.is_video and link.is_playlist: return
        video:YouTube = YouTube(url)
        show_info(video)
        
        text:list[str] = [f"""
Informação do vídeo:
Titulo: {video.title}
Canal: {video.author}
Duração: {str(td(seconds=video.length))}

Thumbnail baixada com sucesso!""", 'success']

        try: download_image(
                video.thumbnail_url,
                ''.join(filter(lambda c: c not in '/|\\?:<>*',video.title)),
                sf.args["path"]
            )
        except Exception as exc:
            text = [f'Não foi possível baixar a Thumbnail.\nCausa do erro: {exc}','error']
            show(text[0]+"\n", text[1])
        Message(*text)

    @with_internet
    def download_audio(sf, url: str) -> None:
        '`Baixa o audio.'
        link:YouTubeLink = YouTubeLink(url)
        if not link.is_video and link.is_playlist: return  
        
        Bar:LoadBar = LoadBar()
        video:YouTube = YouTube(url,
            on_progress_callback= lambda stream,fh,bytes: Bar.update(bytes),
            on_complete_callback= lambda a,b: show("\nBaixado com sucesso!\n")
        )
        if not sf.args['thumbnail']: show_info(video)
        stream:Stream = video.streams.filter(only_audio=True, file_extension='mp4').desc()[0]
        if not stream: raise LiveStreamError

        show("Baixando o audio:")
        Bar.total = stream.filesize
        Bar.update(stream.filesize)
        file:str = stream.download(
            output_path=sf.args["path"],
            filename_prefix=sf.audio_prefix
        )
        text:list[str] = [info(video, Bar.filesize),"success"]

        path:Path = Path(file)
        newpath:Path = path.with_suffix('.mp3')
        if not newpath.exists(): path.rename(newpath)
        else:
            path.unlink()
            text = ['O arquivo já existe!','error']
            show(text[0]+'\n',text[1])
        Message(*text)

    @with_internet
    def download_video(sf,url:str,resolution:str) -> None:
        '`Baixa o vídeo.'
        link:YouTubeLink = YouTubeLink(url)
        if link.is_playlist and not link.is_video: return
        if resolution and not sf.args['audio']: sf.download_audio(url)

        Bar:LoadBar = LoadBar()
        video:YouTube = YouTube(url,
            on_progress_callback= lambda stream,fh, bytes: Bar.update(bytes),
            on_complete_callback= lambda a,b: show("\nBaixado com sucesso!\n")
        )
        if not (sf.args['thumbnail'] or sf.args['audio'] or resolution): show_info(video)
        
        stream:Stream = video.streams.get_highest_resolution() if not resolution \
                        else get_resolution(video.streams, resolution)
        if not stream: raise LiveStreamError

        show("Baixando o vídeo:")
        Bar.total = stream.filesize
        Bar.update(stream.filesize)
        stream.download(
            output_path=sf.args["path"],
            filename_prefix=sf.video_prefix
        )
        Message(info(video, Bar.filesize),"success")

    @with_internet
    def download_play_list(sf, url: str, audio_flag: bool, thumbnail_flag: bool, resolution: str) -> None:
        '`Baixa a Playlist.'
        success = True
        for video in Playlist(url).videos:
            try:
                status:dict = YouTubeLink(video.watch_url).available_for_download
                if not status["available"]:
                    success = error(video,status["error_message"])
                    show("Vídeo pulado.\n","warning")
                    continue
                if thumbnail_flag: sf.download_thumbnail(video.watch_url)
                if audio_flag: sf.download_audio(video.watch_url)
                if not (audio_flag or thumbnail_flag): sf.download_video(video.watch_url, resolution)
            except NoResolutionDesired:
                success = error(video,"O vídeo não tem a resolução selecionada.")
                show("Vídeo pulado.\n","warning")
            except LiveStreamError:
                success = error(video, 'O vídeo é uma estreia e não pôde ser baixado.\n'+
                'Tente novamente mais tarde.\n')
            except KeyboardInterrupt:
                success = error(video,'Interrompido pelo teclado.\n')
            except Exception as exc:
                success = error(video, f"Vídeo indisponível, causa do erro:\n{exc}\n")
        
        text:tuple = ('Playlist baixada com sucesso!', 'success') if success else \
                     ('Não foi possível baixar com sucesso a playlist.','error') 
        Message(*text)

def info(video:YouTube, size:str) -> str:
    '`Retorna as informações do vídeo baixado.'
    return f"""
Informação do vídeo:
Titulo: {video.title}
Canal: {video.author}
Duração: {str(td(seconds=video.length))}
Tamanho: {size}

|{size}| {'█'*30} 100% 

Baixado com sucesso!"""
    
def get_resolution(streams:StreamQuery, resolution:str) -> Stream:
    '`Obtêm as resoluções disponíveis.'
    for stream in streams.filter(res=resolution,adaptive=True,file_extension='mp4').desc():
        if stream.resolution == resolution: return stream
    raise NoResolutionDesired

def show_info(video:YouTube) -> None:
    '`Mostra as informações do vídeo.' 
    print( f"""{colored("Informação do vídeo:","warning")}
{colored("Titulo:")} {video.title}
{colored("Canal:")} {video.author}
{colored("Duração:")} {str(td(seconds=video.length))}\n""" )

def error(video:YouTube, message:str) -> None:
    '`Mostra os erros.'
    show(message,'error')
    Message(video.title+'\n\n'+message,'error')