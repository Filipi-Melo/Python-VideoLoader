'`Módulo criador da barra de carregamento.'
from hurry.filesize import alternative, size
from colorama import init, Fore

class LoadBar:
    '`Classe geradora da barra de carregamento.'
    total:float = 0
    init(autoreset=True)

    def update(sf, remaining: int) -> None:
        '`Atualiza a barra.'
        finished:float = sf.total - remaining
        percent:float = round(100 * finished / sf.total, 1)
        filledLength:int = int(50 * finished // sf.total)

        filled:str = Fore.GREEN + '█' * filledLength + Fore.RESET
        finished_label:str = size(finished, system=alternative)
        sf.filesize:str = size(sf.total, system=alternative)
        
        print(" " * 100,end="\r")
        print(f'\r{finished_label} / {sf.filesize} |{filled.ljust(60,"-")}| {percent} %', end="\r")