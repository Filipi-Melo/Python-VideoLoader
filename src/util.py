'`Import methods module.'
from .printer import Message
from urllib.error import URLError
import re, urllib.request as url, requests

def regex_search(pattern: str, string: str) -> bool:
    '`Check url pattern.'
    regex = re.compile(pattern)
    return regex.search(string)

def is_internet() -> bool:
    '`Tests the connetion.'
    try: return url.urlopen("https://www.google.com/", timeout=1)    
    except URLError: pass

def with_internet(func):
    '`Check your internet connection.'
    def wrapper(*arg, **kwargs):
        return func(*arg, **kwargs) if is_internet() \
        else Message("Internet connection lost.","error")
    return wrapper

def download_image(url: str, name: str, output_folder: str) -> None:
    '`Download image content.'
    with open(f"{output_folder}/{name}.jpg", 'wb') as handler:
        handler.write(requests.get(url).content)