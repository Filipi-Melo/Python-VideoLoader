'`Loading bar creator module.'
from hurry.filesize import alternative,size
from colorama import init,Fore

class LoadBar:
    '`Loading bar generator class.'
    total:float = 0
    init(autoreset=True)

    def update(sf, remaining: int) -> None:
        '`Updates the bar.'
        finished = sf.total - remaining
        percent = round(100 * finished / sf.total, 1)
        filledLength = int(50 * finished // sf.total)

        filled = Fore.GREEN + '█' * filledLength + Fore.RESET
        finished_label = size(finished, system=alternative)
        sf.filesize = size(sf.total, system=alternative)
        
        print(" " * 100,end="\r")
        sf.text = f'\r{finished_label} / {sf.filesize} |{ filled.ljust(60,"-") }| {percent} %'
        print(sf.text, end = "\r")