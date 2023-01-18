'`Módulo gerador de janelas e imprimidor no terminal.'
from colorama import Style,Fore,init
from src.banner import IMAGE
from random import randint
from pathlib import Path
import PySimpleGUI as sg

init(autoreset=True)
styles = {
"success": Fore.GREEN + Style.BRIGHT,
"warning": Fore.YELLOW + Style.BRIGHT,
"error": Fore.RED + Style.BRIGHT}

@staticmethod
def show(text: str, type: str = "success") -> None:
    '`Imprime os textos coloridos.'
    print(f'{ styles[type] }{ text }{ Fore.RESET }'
    if type in styles else text)

@staticmethod
def colored(text: str, type: str = "success") -> str:
    '`Colore os textos.'
    return f'{ styles[type] }{ text }{ Fore.RESET }' if type in styles else text

class Window:
    '`Classe criadora de janelas'
    blue, yellow, white, black= "#000280","#fcd600",'#ffffff','#000000'
    sg.LOOK_AND_FEEL_TABLE['PyVLoaderTheme'] = {
    'BACKGROUND': '#a9b2d1', 'TEXT': black, 'INPUT': white, 
    'TEXT_INPUT': black, 'SCROLL': '#99CC99', 'BUTTON': (white, blue), 
    'PROGRESS': ('#D1826B', '#CC8019'), 'BORDER': 1, 
    'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}
    sg.theme('PyVLoaderTheme')
    
    def create(self,layout:list,show) -> None:
        '`Cria uma nova janela`'
        self.window=sg.Window("Py VLoader 2.0",layout)
        event=True
        while event and event!="OK": 
            event,value = self.window.read(0)
            show(event,value)
        self.window.close()

class Main(Window):
    '`Classe geradora da janela principal'
    def __init__(self,start:object) -> None:
        self.start = start
        self.args={
            'video':False,'audio':False,'thumbnail':False,'path':None,
            'playlist':False,'info':False,'resolution':None,'url':None}
        pdx=11
        expand=[sg.Text("",key=k, expand_x=True) for k in range(4)]
        
        self.layout=[
        [expand[0],sg.Image(IMAGE),expand[1]],
        [expand[2],sg.Text("Baixe videos e músicas do Youtube."),expand[3]],
        
        [sg.Text("Digite a URL:")],
        [sg.InputText(key="url")],
        
        [sg.Text("Digite a pasta de saída (Diretório) :    "),
        sg.FolderBrowse("Procurar",s=(10,0),target="path")],
        [sg.InputText(key="path")],
        
        [sg.Text("Digite a resolução (000p) : opcional")],
        [sg.InputText(key="res")],
        [sg.Text()],
        
        [sg.Button("Video",key="vid",s=(pdx,0)),
        sg.Button("Playlist ",key="pl",s=(12,0)),
        sg.Button("Informação",key="info",s=(pdx,0))],

        [sg.Button("Audio",key="aud",s=(pdx,0)),
        sg.Button("Thumbnail",key="th",s=(12,0)),
        sg.Button("Limpar",key="clear",s=(pdx,0))],

        [sg.Button("Baixar",key="download",s=(12,0),pad=(111,10),button_color=(self.white, '#fc0000'))]]
        self.create(self.layout,self.show)
    
    def update(self,List:list) -> None:
        '`Atualiza os botões na janela'
        for i in range(len(List[0])):
            self.window[List[0][i]].update(button_color=(List[1][i], List[2][i]))
            self.args[List[3][i]]=List[4][i]
    
    def show(self,event,value) -> None:
        '`Atualiza a janela principal'
        if event == "vid": self.update([['vid','pl'],
            [self.black,self.white],[self.yellow,self.blue],
            ['video','playlist'],[True,False]])

        if event == "pl": self.update([['pl','vid'],
            [self.black,self.white],[self.yellow,self.blue],
            ['playlist','video'],[True,False]])

        if event == "aud": self.update([['aud','th','info'],
            [self.black,self.white,self.white],[self.yellow,self.blue,self.blue],
            ['audio','thumbnail','info'],[True,False,False]])

        if event == "info": self.update([['info','th','aud'],
            [self.black,self.white,self.white],[self.yellow, self.blue, self.blue],
            ['info','thumbnail','audio'],[True,False,False]])

        if event == "th": self.update([['th','aud','info'],
            [self.black,self.white,self.white],[self.yellow,self.blue,self.blue],
            ['thumbnail','audio','info'],[True,False,False]])

        if event == "clear": self.update([['vid','pl','aud','th','info'],
            [self.white for _ in range(5)], [self.blue for _ in range(5)],
            ['video','playlist','audio','thumbnail','info'], [False for _ in range(5)]])
        
        if event == "download":
            self.args["url"] = value["url"]
            self.args["path"] = Path(value["path"]) if value["path"] else Path.cwd()
            self.args["resolution"] = value["res"] if value["res"] else None
            self.start(self.args)

class Message(Window):
    '`Classe geradora das janelas de mensagens.'
    def __init__(self,text:str, type:str= None) -> None:
        expand=[sg.Text(" ", key=k, expand_x=True) for k in range(6)]
        
        emoji, num = bytes(0), randint(0,14)
        if type=="error": emoji = sg.EMOJI_BASE64_SAD_LIST[num]
        if type=="success": emoji = sg.EMOJI_BASE64_HAPPY_LIST[num]

        image:list = [expand[2], sg.Image(emoji), expand[3]] if type else []
        self.layout=[
            [expand[0],sg.Text(text),expand[1]],
            image,
            [expand[4],sg.Button("OK"),expand[5]]
        ]
        self.create(self.layout, lambda event, value: None)