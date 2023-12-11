'`Módulo de metódos para importação'
from .printer import show, Message
from urllib.error import URLError
from re import search as regex_search, compile, Pattern
from traceback import print_exc
from datetime import timedelta as td, date
from moviepy import AudioFileClip as Audio, VideoFileClip as Video, ColorClip
import requests, urllib.request as url

BLACK:ColorClip = ColorClip((1,1), duration=0).with_fps(0.5)
RS:Pattern[str] = compile(r'^[\d]{3,4}[p]$')
PL:Pattern[str] = compile(r'list=[\w-]{34}')
VD:Pattern[str] = compile(r'(v=|\/)([\w-]{11})[^\w-]')

def download_image(url:str, name:str, output_folder:str) -> None:
    '`Baixa o conteúdo da imagem.'
    with open(f'{output_folder}/{name}.jpg', 'wb') as file:
        file.write(requests.get(url).content)

def hasconn() -> bool:
    '`Testa a conexão.'
    try: return url.urlopen('https://www.google.com/', timeout=1)    
    except URLError: pass
    except TimeoutError: return hasconn()

def is_res(res:str) -> bool:
    '`Verifica se a resolução é válida.'
    return regex_search(RS, res)

def is_playlist(url:str) -> bool:
    '`Verifica se a url é uma playlist.'
    return regex_search(PL, url)

def is_video(url:str) -> bool:
    '`Verifica se a url é um vídeo.'
    return regex_search(VD, url + ' ')

def formatURL(url:str) -> str:
    '`Formata a url crua.'
    if len(url) == 11 and is_video('v=' + url): 
        return 'https://www.youtube.com/watch?v=' + url
    elif len(url) == 34 and is_playlist('list=' + url): 
        return 'https://www.youtube.com/playlist?list=' + url
    return url

def dateform(date:date) -> str:
    try: return date.strftime('%d/%m/%Y')
    except AttributeError: return None

def length(seconds:int) -> td: return td(seconds=seconds)

def unifyclips(videofile:str, audiofile:str, output:str):
    '`Unifica o vídeo e audio.'
    clip:Video|ColorClip = Video(videofile) if videofile else BLACK
    clip.audio = Audio(audiofile)
    clip.write_videofile(output, logger=None)
    clip.close()
    show('Pronto!'.ljust(25))

def with_internet(function):
    '`Verifica a conexão de internet.'
    def inner(*args, **kwargs):
        if hasconn(): return function(*args, **kwargs)
        Message('Conexão com a internet perdida.','error')
    return inner