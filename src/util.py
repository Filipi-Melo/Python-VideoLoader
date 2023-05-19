'`Módulo de metódos para importação'
from .printer import Message
from urllib.error import URLError
import re, urllib.request as url, requests

def download_image(url:str, name:str, output_folder:str) -> None:
    '`Baixa o conteúdo da imagem.'
    with open(f'{output_folder}/{name}.jpg', 'wb') as handler:
        handler.write(requests.get(url).content)

def is_internet() -> bool:
    '`Testa a conexão.'
    try: return url.urlopen("https://www.google.com/", timeout=1)    
    except URLError: pass

def regex_search(pattern:str, string:str) -> bool:
    '`Verifica o padrão da url.'
    regex = re.compile(pattern)
    return regex.search(string)

def Urlformat(url:str,pl:bool) -> str:
    '`Formata a url crua.'
    if not pl and len(url) == 11: url = "https://www.youtube.com/watch?v=" + url
    elif len(url) == 34: url = "https://www.youtube.com/watch?&list=" + url
    return url

def with_internet(function):
    '`Verifica a conexão de internet.'
    def inner(*args, **kwargs):
        if is_internet(): return function(*args, **kwargs)
        else: Message("Conexão com a internet perdida.","error")
    return inner