"""==[DOC-FILE]===============================================================
Arquivo : src/infraestrutura/retencao_artefatos.py
Classe  : -
Pacote  : src.infraestrutura
Modulo  : Infraestrutura - Retencao de Artefatos

Papel   : Aplica limites de crescimento para screenshots, logs CSV, logs de
          texto e traces JSON, evitando acumulo indefinido em producao.

Conecta com:
- pathlib - acesso a arquivos e diretorios
- csv/json - reescrita controlada de artefatos estruturados

Fluxo geral:
1) Mantem apenas os arquivos mais recentes em diretorios monitorados.
2) Reduz CSVs e logs textuais para o limite configurado.
3) Reduz listas JSON persistidas para os registros mais recentes.
[DOC-FILE-END]==============================================================="""

from __future__ import annotations

import csv
import json
from collections import deque
from pathlib import Path
from typing import Iterable


def manter_arquivos_mais_recentes(
    diretorio: Path,
    max_arquivos: int,
    padroes: Iterable[str] = ("*",),
) -> None:
    if max_arquivos <= 0 or not diretorio.exists():
        return

    arquivos_unicos: dict[Path, float] = {}
    for padrao in padroes:
        for caminho in diretorio.glob(padrao):
            if caminho.is_file():
                arquivos_unicos[caminho] = caminho.stat().st_mtime

    arquivos_ordenados = sorted(
        arquivos_unicos.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    for caminho, _ in arquivos_ordenados[max_arquivos:]:
        try:
            caminho.unlink(missing_ok=True)
        except OSError:
            continue


def limitar_csv_por_registros(
    caminho_arquivo: Path,
    max_registros: int,
    delimitador: str = ";",
) -> None:
    if max_registros <= 0 or not caminho_arquivo.exists():
        return

    try:
        with caminho_arquivo.open("r", newline="", encoding="utf-8") as arquivo_csv:
            linhas = list(csv.reader(arquivo_csv, delimiter=delimitador))
    except OSError:
        return

    if not linhas:
        return

    cabecalho = linhas[0]
    registros = linhas[1:]
    if len(registros) <= max_registros:
        return

    registros_recentes = registros[-max_registros:]
    try:
        with caminho_arquivo.open("w", newline="", encoding="utf-8") as arquivo_csv:
            escritor = csv.writer(arquivo_csv, delimiter=delimitador)
            escritor.writerow(cabecalho)
            escritor.writerows(registros_recentes)
    except OSError:
        return


def limitar_texto_por_linhas(caminho_arquivo: Path, max_linhas: int) -> None:
    if max_linhas <= 0 or not caminho_arquivo.exists():
        return

    try:
        with caminho_arquivo.open("r", encoding="utf-8") as arquivo_texto:
            linhas = deque(arquivo_texto, maxlen=max_linhas)
    except OSError:
        return

    try:
        with caminho_arquivo.open("w", encoding="utf-8") as arquivo_texto:
            arquivo_texto.writelines(linhas)
    except OSError:
        return


def limitar_json_lista(caminho_arquivo: Path, max_itens: int) -> None:
    if max_itens <= 0 or not caminho_arquivo.exists():
        return

    try:
        conteudo = json.loads(caminho_arquivo.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    if not isinstance(conteudo, list) or len(conteudo) <= max_itens:
        return

    try:
        caminho_arquivo.write_text(
            json.dumps(conteudo[-max_itens:], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        return
