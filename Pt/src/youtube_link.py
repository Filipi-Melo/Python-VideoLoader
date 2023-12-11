'`Módulo gerenciador de links do youtube.'
from .exceptions import *
from .util import is_playlist, is_video, print_exc, with_internet
from pytube import extract, request, Playlist

ERRORS:dict[str, type[Exception]] = {
    'NO_PLAYLIST':PlaylistUnavailable, 'INVALID_URL':InvalidURL, 
    'UNPLAYABLE':VideoUnavailable, 'ERROR':VideoUnavailable,
    'LIVE_STREAM':LiveStreamError,
}

class YouTubeLink:
    '`Classe verificadora de links.'
    def __init__(sf) -> None:
        sf.status:str = None
        sf.message:str = None
    
    def start(sf, url:str) -> None:
        '`Guarda a url.'
        sf.status = None
        sf.url:str = url

    @property
    def is_video(sf) -> bool:
        return is_video(sf.url)
    
    @property
    def is_playlist(sf) -> bool:
        return is_playlist(sf.url)
    
    @property
    def is_available(sf) -> bool:
        '`Verifica o estado da url.'
        try: sf.test_url()
        except InternetError:
            sf.message = 'Conexão com a internet perdida.'
        except InvalidURL:
            sf.message = f'Foi providenciada uma url inválida "{sf.url}".'
        except LiveStreamError:
            sf.message = 'O video é uma estreia ao vivo e não pode ser baixado.'
        except VideoUnavailable:
            sf.message = 'O video não está disponível para download, possíveis razões: apenas membros, restrito.'
        except PlaylistUnavailable:
            sf.message = 'A playlist não está disponível.'
        else: return True

    @property
    def check_availability(sf) -> None:
        '`Verifica o estado do vídeo.'
        watch_url:str = f'https://youtube.com/watch?v={extract.video_id(sf.url)}'
        sf.status = extract.playability_status(request.get(watch_url))[0]

    @with_internet
    def test_url(sf) -> None:
        '`Testa a url.'
        try:
            if not (sf.is_video or sf.is_playlist): sf.status = 'INVALID_URL'
            elif sf.is_video: sf.check_availability
            elif sf.is_playlist and not Playlist(sf.url): sf.status = 'NO_PLAYLIST'
        except Exception:
            print_exc()
            raise InternetError
        if sf.status in ERRORS: raise ERRORS[sf.status]