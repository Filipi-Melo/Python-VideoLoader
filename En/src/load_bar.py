'`Loading bar creator module.'
from hurry.filesize import size
from colorama import init, Fore, Style

class LoadBar:
    '`Loading bar generator class.'
    total:int = 0
    size:str = ''
    init(autoreset=True)

    def update(sf, remaining:int) -> None:
        '`Updates the bar.'
        finished:int = sf.total - remaining
        filled:str = Fore.GREEN + '█' * int(50 * finished // sf.total) + Fore.RESET
        downloaded:str = size(finished)
        
        print(' ' * 100, end='\r')
        print(f'{downloaded} / {sf.size} [{filled.ljust(60,"-")}] {100 * finished / sf.total:.1f} %', end='\r')
    
    def start(sf, filesize:int) -> None:
        '`Starts the bar.'
        sf.total = filesize
        sf.size = size(sf.total)
        sf.update(filesize)

    def onprogress(sf, stream, fh, bytes:int) -> None: sf.update(bytes)
    
    def oncomplete(*args) -> None: print(f'{Fore.GREEN + Style.BRIGHT}\nDownloaded successfully!\n{Fore.RESET}')