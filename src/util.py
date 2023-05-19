'`Import methods module.'
from .printer import Message
from urllib.error import URLError
import re, urllib.request as url, requests

def download_image(url:str, name:str, output_folder:str) -> None:
    '`Download image content.'
    with open(f"{output_folder}/{name}.jpg", 'wb') as handler:
        handler.write(requests.get(url).content)

def is_internet() -> bool:
    '`Tests the connetion.'
    try: return url.urlopen("https://www.google.com/", timeout=1)    
    except URLError: pass

def regex_search(pattern:str, string:str) -> bool:
    '`Check url pattern.'
    regex = re.compile(pattern)
    return regex.search(string)

def Urlformat(url:str, pl:bool) -> str:
    '`Formats the raw url.'
    if not pl and len(url) == 11: url = "https://www.youtube.com/watch?v=" + url
    elif len(url) == 34: url = "https://www.youtube.com/watch?&list=" + url
    return url

def with_internet(function):
    '`Check your internet connection.'
    def inner(*args, **kwargs):
        if is_internet(): return function(*args, **kwargs)
        else: Message("Internet connection lost.","error")
    return inner