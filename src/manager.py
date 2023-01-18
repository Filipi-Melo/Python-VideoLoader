'`Módulo gerenciador de urls e downloads.'
from .util import regex_search,with_internet
from .youtube_link import YouTubeLink
from .downloader import Downloader
from .printer import Message
from .exceptions import *
from pytube import YouTube, Playlist
from datetime import timedelta as td
from pathlib import Path

class Manager:
    '`Classe gerenciadora de downloads.'
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

            except NoResolutionDesired: Message("O vídeo não tem a resolução selecionada.","error")
            except LiveStreamError: Message("""O vídeo é uma estreia e não pôde ser baixado.
               Tente novamente mais tarde.""","error")
            
            if self.args["playlist"]: link.download_play_list(self.args["url"], self.args["audio"],
            self.args["thumbnail"], self.args["resolution"])

        except KeyboardInterrupt: Message('Interrompido pelo teclado.','error')
        except BaseException as exc: Message(f"URL indisponível, causa do erro:\n{exc}","error")

    @property
    def invalid_args(self) -> Message:
        'Verifica os argumentos.'
        empty:bool = True if True not in [self.args[i] for i in \
        ['video','playlist','audio','thumbnail','info']] else False
        
        if empty: return Message('Selecione um botão.','error')

        link = YouTubeLink(self.args["url"])
        status = link.available_for_download
        if not status["available"]:
            return Message(status["error_message"],"error")
        
        if self.args["playlist"] and not link.is_playlist: 
            return Message("Sinalizador de playlist fornecido, mas é a url de vídeo.","error")
        
        if self.args["resolution"] and not regex_search(r"^[\d]{3,4}[p]$",self.args["resolution"]): 
            return Message(f'Foi providenciada resolução inválida "{self.args["resolution"]}".',"error")
        
        if not Path.is_dir(self.args["path"]):
            return Message(f'Foi providenciado diretório inválido "{self.args["path"]}".',"error")

    @with_internet
    def complete_info(sf, url: str) -> None:
        if sf.args["playlist"]: return sf.show_playlist_info(url)
        sf.show_video_info(url)

    def show_video_info(sf, url: str) -> None:
        'Pesquisa e mostra as informações do vídeo.'
        video = YouTube(url)
        resolutions = sf.available_resolutions(url)
        info = f"""
Informação do video:
Titulo: {video.title}
Canal: {video.author}
Visualizações: {video.views}
Duração: {str(td(seconds=video.length))}
Progressivo: {" ".join(resolutions["progressive"])}
Adaptável: {" ".join(resolutions["adaptive"])}
Audio: {" ".join(resolutions["audio"])} """
        Message(info)

    def show_playlist_info(sf, url: str) -> None:
        'Pesquisa e mostra as informações da playlist.'
        playlist = Playlist(url)
        try: channel=f"\nCanal: {playlist.owner}"
        except: channel=""
        info = f"""
Informação da playlist:
Titulo: {playlist.title} {channel}
Visualizações: {playlist.views}
Videos: {playlist.length}"""
        Message(info)
        
    @with_internet
    def available_resolutions(sf, url: str) -> dict:
        'Retorna as resoluções diponíveis.'
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