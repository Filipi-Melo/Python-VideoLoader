'`Import methods module.'
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
    '`Download image content.'
    with open(f'{output_folder}/{name}.jpg', 'wb') as file:
        file.write(requests.get(url).content)

def hasconn() -> bool:
    '`Tests the connetion.'
    try: return url.urlopen('https://www.google.com/', timeout=1)    
    except URLError: pass
    except TimeoutError: return hasconn()

def is_res(res:str) -> bool:
    '`Checks if the resolution is valid.'
    return regex_search(RS, res)

def is_playlist(url:str) -> bool:
    '`Checks if the url is a playlist.'
    return regex_search(PL, url)

def is_video(url:str) -> bool:
    '`Checks if the url is a video.'
    return regex_search(VD, url + ' ')

def formatURL(url:str) -> str:
    '`Formats the raw url.'
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
    '`Unifies video and audio.'
    clip:Video|ColorClip = Video(videofile) if videofile else BLACK
    clip.audio = Audio(audiofile)
    clip.write_videofile(output, logger=None)
    clip.close()
    show('Done!'.ljust(25))

def with_internet(function):
    '`Check the internet connection.'
    def inner(*args, **kwargs):
        if hasconn(): return function(*args, **kwargs)
        Message('Internet connection lost.','error')
    return inner