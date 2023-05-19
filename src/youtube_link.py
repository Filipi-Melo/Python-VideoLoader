'`Módulo gerenciador de links do youtube.'
from .exceptions import *
from .util import regex_search
from pytube import extract,request,Playlist

class YouTubeLink:
    '`Classe verificadora de links.'
    def __init__(sf, url: str) -> None:
        sf.url, sf.status = url,None

    @property
    def check_video_availability(sf):
        '`Verifica o estado do vídeo.'
        video_id = extract.video_id(sf.url)
        watch_url = f"https://youtube.com/watch?v={video_id}"
        sf.status = extract.playability_status(request.get(url=watch_url))[0]
    
    @property
    def is_video(sf) -> bool:
        return regex_search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", sf.url)

    @property
    def is_playlist(sf) -> bool:
        return regex_search(r"(?:list=)([0-9A-Za-z_-]{11}).*", sf.url)

    @property
    def test_url(sf) -> None:
        '`Testa a url.'
        if not (sf.is_video or sf.is_playlist): raise InvalidURL
        try:
            if sf.is_video: sf.check_video_availability
            if sf.is_playlist and not Playlist(sf.url).videos: sf.status = 'NO_PLAYLIST'
        except: raise InternetError
        errors:dict = {'NO_PLAYLIST':PlaylistUnavailable,
                       'UNPLAYABLE':VideoUnavailable,
                       'LIVE_STREAM':LiveStreamError}
        if sf.status in errors: raise errors[sf.status]
        
    @property
    def available_for_download(sf) -> dict:
        '`Verifica o estado da url.'
        available_flag:bool = True
        error_message:str = None

        try: sf.test_url
        except InternetError:
            available_flag = False
            error_message = f'Conexão com a internet perdida.'
        except InvalidURL:
            available_flag = False
            error_message = f'Foi providenciada uma url inválida "{sf.url}".'
        except LiveStreamError:
            available_flag = False
            error_message = 'O video é uma estreia ao vivo e não pode ser baixado.'
        except VideoUnavailable:
            available_flag = False
            error_message = 'O video não está disponível para download, possíveis razões (apenas membros, privado).'
        except PlaylistUnavailable:
            available_flag = False
            error_message = 'A playlist não está disponível.'
        return {"available": available_flag,"error_message": error_message}