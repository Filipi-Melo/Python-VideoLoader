'`Module for generating windows and printing in the terminal.'
from colorama import Style, Fore, init
from .banner import IMAGE
from random import randint
from PySimpleGUI import *

init(autoreset=True)
styles = {
    "success": Fore.GREEN + Style.BRIGHT,
    "warning": Fore.YELLOW + Style.BRIGHT,
    "error": Fore.RED + Style.BRIGHT
}

def show(text: str, type: str = "success") -> None:
    '`Print the texts in color.'
    print(f'{ styles[type] }{ text }{ Fore.RESET }'
        if type in styles else text)

def colored(text: str, type: str = "success") -> str:
    '`Color the texts.'
    return f'{ styles[type] }{ text }{ Fore.RESET }' if type in styles else text

class Windows:
    '`Window creator class.`'
    blue, yellow, white, black= "#000280","#fcd600",'#ffffff','#000000'
    LOOK_AND_FEEL_TABLE['PyVLoaderTheme'] = {
    'BACKGROUND': '#a9b2d1', 'TEXT': black, 'INPUT': white, 
    'TEXT_INPUT': black, 'SCROLL': '#99CC99', 'BUTTON': (white, blue), 
    'PROGRESS': ('#D1826B', '#CC8019'), 'BORDER': 1, 
    'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}
    theme('PyVLoaderTheme')
    windows, call = [],{}
    
    def create(sf, layout:list, show) -> Window:
        '`Create a new window.`'
        window = Window("Py VLoader 2.0", layout, finalize=True,)
        sf.windows.append(window), sf.call.update({str(window):show})
        return window

    def loop(sf) -> None:
        '`Starts the windows.`'
        while 1:
            window, event, value = read_all_windows()
            if event and event != 'OK': sf.call[str(window)](event, value)
            else:
                if window == sf.windows[0]: break
                window.close(), sf.windows.remove(window), sf.call.pop(str(window))

class Main(Windows):
    '`Main window generator class.'
    def __init__(sf,start:object) -> None:
        sf.start, pdx = start, 11
        sf.args:dict[str] = {
            'video':False,'audio':False,'thumbnail':False,'path':None,
            'playlist':False,'info':False,'resolution':None,'url':None
        }
        expand = [Text("",key=k, expand_x=True) for k in range(4)]
        sf.layout = (
            [expand[0],Image(IMAGE),expand[1]],
            [expand[2],Text("Download videos and musics from Youtube."),expand[3]],
            
            [Text("Enter URL:")],
            [InputText(key="url")],
            
            [Text("Enter the output folder (Directory) :    "),
             FolderBrowse("Search",s=(10,0),target="path")],
            [InputText(key="path")],
            
            [Text("Enter resolution (000p): optional")],
            [InputText(key="res")],
            [Text()],
            
            [Button("Video",key="vid",s=(pdx,0)),
             Button("Playlist ",key="pl",s=(12,0)),
             Button("Information",key="info",s=(pdx,0))],

            [Button("Audio",key="aud",s=(pdx,0)),
             Button("Thumbnail",key="th",s=(12,0)),
             Button("Clear",key="clear",s=(pdx,0))],

            [Button("Download",key="download",s=(12,0),pad=(111,10),button_color=(sf.white, '#fc0000'))]
        )
        sf.window = sf.create(sf.layout, sf.show)
        sf.loop()

    def update(sf,List:list) -> None:
        '`Updates the buttons in the window.'
        for i in range(len(List[0])):
            sf.window[List[0][i]].update(button_color=(List[1][i], List[2][i]))
            sf.args[List[3][i]] = List[4][i]
    
    def show(sf,event,value) -> None:
        '`Updates the main window.'
        if event == "vid": sf.update((('vid','pl'),
            (sf.black,sf.white),(sf.yellow,sf.blue),
            ('video','playlist'),(True,False)))

        if event == "pl": sf.update((('pl','vid'),
            (sf.black,sf.white),(sf.yellow,sf.blue),
            ('playlist','video'),(True,False)))

        if event == "aud": sf.update((('aud','info'),
            (sf.black,sf.white),(sf.yellow,sf.blue),
            ('audio','info'),(True,False)))

        if event == "info": sf.update((('info','th','aud'),
            (sf.black,sf.white,sf.white),(sf.yellow, sf.blue, sf.blue),
            ('info','thumbnail','audio'),(True,False,False)))

        if event == "th": sf.update((('th','info'),
            (sf.black,sf.white),(sf.yellow,sf.blue),
            ('thumbnail','info'),(True,False)))

        if event == "clear": sf.update((('vid','pl','aud','th','info'), [sf.white]*5,
            [sf.blue]*5, ('video','playlist','audio','thumbnail','info'), [False]*5))
        
        if event == "download":
            sf.args["url"] = value["url"]
            sf.args["path"] = value["path"]
            sf.args["resolution"] = value["res"] if value["res"] else None
            sf.start(sf.args)

class Message(Windows):
    '`Generator class for message windows.'
    def __init__(sf, text:str, type:str = None) -> None:
        expand = [Text(" ", key=k, expand_x=True) for k in range(6)]
        num = randint(0,14)
        emojis = {'success':EMOJI_BASE64_HAPPY_LIST[num], 'error':EMOJI_BASE64_SAD_LIST[num]} 

        sf.layout = (
            [expand[0], Text(text), expand[1]],
            [expand[2], Image(emojis[type]), expand[3]] if type in emojis else [],
            [expand[4], Button("OK"), expand[5]]
        )
        sf.create(sf.layout, lambda event, value: None)