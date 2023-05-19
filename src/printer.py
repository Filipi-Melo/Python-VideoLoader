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
    register:dict[str,dict] = {}
    id:int = 0

    @classmethod
    def create(cls,layout:list, show) -> Window:
        '`Create a new window.`'
        window:Window = Window("Py VLoader 2.0", layout, finalize=True,)
        cls.register.update({str(window):{'id':cls.id, 'call':show}})
        Windows.id += 1
        return window

    def loop(sf) -> None:
        '`Starts the windows.`'
        while True:
            window, event, value = read_all_windows()
            if event and event != 'OK': sf.register[str(window)]['call'](event, value)
            else:
                if not sf.register[str(window)]['id']: break
                window.close()
                sf.register.pop(str(window))

class Main(Windows):
    '`Main window generator class.'
    def __init__(sf,start:object) -> None:
        sf.start, pdx = start, 11
        sf.args:dict = {
            'video':False,'audio':False,'thumbnail':False,'path':None,
            'playlist':False,'info':False,'resolution':None,'url':None
        }
        expand = [Text("",key=k, expand_x=True) for k in range(4)]
        sf.layout = [
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
        ]
        sf.window = sf.create(sf.layout, sf.show)
        sf.loop()

    def update(sf,*args:list) -> None:        
        '`Updates the buttons in the window.'
        for List in args:
            sf.window[List[0]].update(button_color=(List[1], List[2]))
            sf.args[List[3]] = List[4]

    def show(sf,event:str,value:dict) -> None:
        '`Updates the main window.'
        match event:
            case "aud": sf.update(['aud',sf.black,sf.yellow,'audio',True],
                                   ['info',sf.white,sf.blue,'info',False])
            case "clear": sf.update(['vid',sf.white,sf.blue,'video',False], ['pl',sf.white,sf.blue,'playlist',False],
                                    ['aud',sf.white,sf.blue,'audio',False], ['th',sf.white,sf.blue,'thumbnail',False],
                                    ['info',sf.white,sf.blue,'info',False])
            case "download":
                sf.args["url"] = value["url"]
                sf.args["path"] = value["path"]
                sf.args["resolution"] = value["res"] if value["res"] else None
                sf.start(sf.args)
            case "info": sf.update(['info',sf.black,sf.yellow,'info',True], ['th',sf.white,sf.blue,'thumbnail',False],
                                   ['aud',sf.white,sf.blue,'audio',False])
            case "pl": sf.update(['pl',sf.black,sf.yellow,'playlist',True], ['vid',sf.white,sf.blue,'video',False])
            case "th": sf.update(['th',sf.black,sf.yellow,'thumbnail',True], ['info',sf.white,sf.blue,'info',False])
            case "vid": sf.update(['vid',sf.black,sf.yellow,'video',True], ['pl',sf.white,sf.blue,'playlist',False])

class Message(Windows):
    '`Generator class for message windows.'
    def __init__(sf, text:str, type:str = None) -> None:
        expand:list = [Text(" ", key=K, expand_x=True) for K in range(6)]
        num:int = randint(0,14)
        emojis:dict = {'success':EMOJI_BASE64_HAPPY_LIST[num], 'error':EMOJI_BASE64_SAD_LIST[num]} 

        layout:list = [
            [expand[0], Text(text), expand[1]],
            [expand[2], Image(emojis[type]), expand[3]] if type in emojis else [],
            [expand[4], Button("OK"), expand[5]]
        ]
        sf.create(layout, lambda event, value: None)