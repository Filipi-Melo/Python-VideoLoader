'`Módulo de metódos para importação'
from .printer import Message
from urllib.error import URLError
import re, urllib.request as url, requests
from pathlib import Path

def regex_search(pattern: str, string: str) -> bool:
    '`Verifica o padrão da url.'
    regex = re.compile(pattern)
    return regex.search(string)

def is_internet() -> bool:
    '`Testa a conexão.'
    try: return url.urlopen("https://www.google.com/", timeout=1)    
    except URLError: pass

def with_internet(func):
    '`Verifica a conexão de internet.'
    return lambda *args, **kwargs: func(*args, **kwargs) if is_internet() \
        else (None, Message("Conexão com a internet perdida.","error"))[0]

def download_image(url: str, name: str, output_folder: str) -> None:
    '`Baixa o conteúdo da imagem.'
    with open(f'{output_folder}\{name}.jpg', 'wb') as handler:
        handler.write(requests.get(url).content)