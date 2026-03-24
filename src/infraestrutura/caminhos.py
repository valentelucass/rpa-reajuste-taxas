"""==[DOC-FILE]===============================================================
Arquivo : src/infraestrutura/caminhos.py
Classe  : -
Pacote  : src.infraestrutura
Modulo  : Infraestrutura - Resolucao de Caminhos

Papel   : Separa o diretorio da aplicacao do diretorio real dos recursos
          para manter fontes, logo e icones acessiveis em execucao local
          e no pacote gerado pelo PyInstaller.
[DOC-FILE-END]==============================================================="""

import sys
from pathlib import Path


def resolver_diretorio_aplicacao() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resolver_diretorio_recursos() -> Path:
    if getattr(sys, "frozen", False):
        caminho_meipass = getattr(sys, "_MEIPASS", "")
        if caminho_meipass:
            return Path(caminho_meipass).resolve()
        return resolver_diretorio_aplicacao()
    return Path(__file__).resolve().parents[2]


DIRETORIO_APLICACAO = resolver_diretorio_aplicacao()
DIRETORIO_RECURSOS = resolver_diretorio_recursos()


def resolver_caminho_recurso(*partes: str) -> Path:
    return resolver_diretorio_recursos().joinpath(*partes)
