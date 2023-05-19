'`Loading bar creator module.'
from hurry.filesize import alternative, size
from colorama import init, Fore

class LoadBar:
    '`Loading bar generator class.'
    total:float = 0
    init(autoreset=True)

    def update(sf, remaining: int) -> None:
        '`Updates the bar.'
        finished:float = sf.total - remaining
        percent:float = round(100 * finished / sf.total, 1)
        filledLength:int = int(50 * finished // sf.total)

        filled:str = Fore.GREEN + '█' * filledLength + Fore.RESET
        finished_label:str = size(finished, system=alternative)
        sf.filesize:str = size(sf.total, system=alternative)
        
        print(" " * 100,end="\r")
        print(f'\r{finished_label} / {sf.filesize} |{filled.ljust(60,"-")}| {percent} %', end="\r")