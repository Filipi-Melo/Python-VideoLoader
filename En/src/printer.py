'`Module for generating windows and printing in the terminal.'
from typing import Any, Callable, Iterable, TypeVar
from .banner import BANNER
from colorama import Style, Fore, init
from itertools import count
from random import randint
from PySimpleGUI import (
    Any, Button, Checkbox, Element, Image, Input, Radio, Text, Window, 
    EMOJI_BASE64_HAPPY_LIST, EMOJI_BASE64_SAD_LIST, LOOK_AND_FEEL_TABLE, 
    FolderBrowse, read_all_windows, theme
)

ids:count = count()
init(True)

styles:dict[str, str] = {
    'success': Fore.GREEN + Style.BRIGHT,
    'warning': Fore.YELLOW + Style.BRIGHT,
    'error': Fore.RED + Style.BRIGHT
}

def colored(text:str, type:str = 'success') -> str:
    '`Color the texts.'
    return f'{styles[type]}{text}{Fore.RESET}' if type in styles else text

def show(text:str, type:str = 'success') -> None:
    '`Print the texts in color.'
    print(colored(text, type))

def close(func:Callable) -> Callable:
    '`Closes the program if desired.'
    def wrapper(*args):
        try: func(*args)
        except KeyboardInterrupt: pass
    return wrapper

def justify(text:str|Any, element:type[Element] = Text) -> tuple[Text,Element,Text]:
    '`Justifies the text.'
    return Text(expand_x=True), element(text), Text(expand_x=True)

class Windows(Window):
    '`Window creator class.'
    blue, white, black= '#000280', '#ffffff','#000000'
    
    LOOK_AND_FEEL_TABLE['PyVLoaderTheme'] = {
        'BACKGROUND': '#a9b2d1', 'TEXT': black, 'INPUT': white, 
        'TEXT_INPUT': black, 'SCROLL': '#99CC99', 'BUTTON': (white, blue), 
        'PROGRESS': ('#D1826B', '#CC8019'), 'BORDER': 1, 
        'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0
    }

    def __init__(sf, call:Callable, *args, **kwargs) -> None:
        super().__init__('Python VideoLoader 2.0', *args, finalize=True, **kwargs)
        sf.call:Callable = call
        sf.id:int = next(ids)
    
    @close
    def run(sf) -> None:
        '`Starts the windows.`'
        while True:
            window, event, value = read_all_windows()
            if event and event != 'OK':
                window.call(value)
                continue
            if not window.id: break
            window.close()

theme('PyVLoaderTheme')

class Main(Windows):
    '`Main window generator class.'
    def __init__(sf, call:Callable) -> None:
        styles:dict[str, Any] = {'s':(9,0), 'background_color':sf.blue, 'text_color':sf.white}

        layout:list[Iterable[Element]] = [
            justify(BANNER, Image),
            justify('Download videos and musics from Youtube.'),
            [Text('Enter URL:')],
            [Input(key='url')],
            [
             Text('Enter the output folder (Directory) :    '),
             FolderBrowse('Search', s=(10,0), target='path')
            ],
            [Input(key='path')],
            [Text('Enter resolution (000p): optional')],
            [Input(key='resolution')],
            [Text()],
            [
             Radio('Video', 1, key='video', **styles),
             Radio('Playlist', 1, key='playlist', **styles),
             Checkbox('Info', key='info', **styles)
            ],
            [
             Checkbox('Audio', key='audio', **styles),
             Checkbox('Thumbnail', key='thumbnail', **styles),
             Button('Download', key='download', s=(11,0), button_color=(sf.white, '#fc0000'))
            ]
        ]
        super().__init__(call, layout)
        sf.run()

class Message(Windows):
    '`Generator class for message windows.'
    emojis:dict[str,list[bytes]] = {'success':EMOJI_BASE64_HAPPY_LIST, 'error':EMOJI_BASE64_SAD_LIST} 
    
    def __init__(sf, text:str|list[str], type:str = None, split:int = None) -> None:
        num:int = randint(0, 14)
        
        if split == 1:
            head, *mid, end = text.splitlines()
            text = head, '\n'.join(mid), end
        elif split == 2:
            head, *mid, bar, end = text.splitlines()
            text = head, '\n'.join(mid), bar, end

        layout:list[Iterable[Element]] = [
            justify(text) if isinstance(text, str) else map(justify, text),
            justify(sf.emojis[type][num], Image) if type in sf.emojis else (),
            justify('OK', Button)
        ]
        super().__init__(lambda _:None, layout, resizable=True)