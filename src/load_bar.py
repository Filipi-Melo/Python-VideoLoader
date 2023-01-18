'`Módulo criador da barra de carregamento.'
from hurry.filesize import alternative,size
from colorama import init,Fore

class LoadBar:
    '`Classe geradora da barra de carregamento:'
    total_size:float = 0
    init(autoreset=True)
    def update(self, remaining: int) -> None:
        '`Atualiza a barra:'
        finished = self.total_size - remaining
        percent = round(100 * finished / self.total_size, 1)
        filledLength = int(50 * finished // self.total_size)

        filled = Fore.GREEN +  '█' * filledLength + Fore.RESET 
        not_filled = "-" * (50 - filledLength) 

        finished_label =  size(finished,system=alternative)
        self.filesize =  size(self.total_size,system=alternative)
        
        print(" " * 100,end="\r")
        self.text=f'\r{finished_label} / {self.filesize} |{ filled + not_filled}| {percent} %'
        print(self.text, end = "\r")