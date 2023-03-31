'`Módulo gerenciador de urls e downloads.'
from .exceptions import NoResolutionDesired, LiveStreamError
from .util import regex_search, with_internet, Urlformat
from .youtube_link import YouTubeLink
from .downloader import Downloader
from .printer import Message
from datetime import timedelta as td
from pytube import YouTube, Playlist
from pathlib import Path

class Manager:
    '`Classe gerenciadora de downloads.'
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
            except NoResolutionDesired: Message("O vídeo não tem a resolução selecionada.","error")
            except LiveStreamError: Message("""O vídeo é uma estreia e não pôde ser baixado.
               Tente novamente mais tarde.""","error")
            
            if sf.args["playlist"]: link.download_play_list( sf.args["url"], sf.args["audio"],
               sf.args["thumbnail"], sf.args["resolution"])
        except KeyboardInterrupt: Message('Interrompido pelo teclado.','error')
        except Exception as exc: Message(f"URL indisponível, causa do erro:\n{exc}","error")

    @property
    def invalid_args(sf) -> Message:
        '`Verifica os argumentos.'
        if not len([*filter(lambda i: sf.args[i], ('video','playlist','audio','thumbnail','info'))]): 
            return Message('Selecione um botão.','error')

        link = YouTubeLink(sf.args["url"])
        status = link.available_for_download
        if not status["available"]:
            return Message(status["error_message"],"error")

        if sf.args["playlist"] and not link.is_playlist: 
            return Message("Sinalizador de playlist fornecido, mas é a url de vídeo.","error")

        if sf.args["resolution"] and not regex_search(r"^[\d]{3,4}[p]$",sf.args["resolution"]): 
            return Message(f'Foi providenciada resolução inválida "{sf.args["resolution"]}".',"error")

        if not Path.is_dir(sf.args["path"]):
            return Message(f'Foi providenciado diretório inválido "{sf.args["path"]}".',"error")

    @property
    @with_internet
    def complete_info(sf) -> None:
        if sf.args["playlist"]: return sf.show_playlist_info(sf.args['url'])
        sf.show_video_info(sf.args['url'])

    @staticmethod
    def show_video_info(url: str) -> None:
        '`Pesquisa e mostra as informações do vídeo.`'
        video = YouTube(url)
        progressive = video.streams.filter(progressive=True, file_extension='mp4').desc()
        adaptive = video.streams.filter(only_video=True,adaptive=True, file_extension='mp4').asc()
        audio = video.streams.filter(only_audio=True, file_extension='mp4').desc()
    
        Message( f"""
Informação do video:
Titulo: {video.title}.
Canal: {video.author}.
Visualizações: {video.views:,}.
Duração: {str(td(seconds=video.length))}.
Progressivo: {", ".join({}.fromkeys( map(lambda stream: stream.resolution, progressive)))}.
Adaptável: {", ".join({}.fromkeys( map(lambda stream: stream.resolution, adaptive)))}.
Audio: {", ".join({}.fromkeys( map(lambda stream: stream.abr, audio)))}.""" )

    @staticmethod
    def show_playlist_info(url: str) -> None:
        '`Pesquisa e mostra as informações da playlist.'
        playlist = Playlist(url)
        try: channel = f"\nCanal: {playlist.owner}."
        except: channel = ""

        Message( f"""
Informação da playlist:
Titulo: {playlist.title}.{channel}
Visualizações: {playlist.views:,}.
Videos: {playlist.length}.""" )