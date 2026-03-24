"""==[DOC-FILE]===============================================================
Arquivo : main.py
Classe  : -
Pacote  : raiz do projeto
Modulo  : Bootstrap da Aplicacao Desktop

Papel   : Inicializa a aplicacao PySide6, configura identidade visual basica
          e abre a janela principal do painel de automacao.

Conecta com:
- src.ui.ui_main - janela principal do dashboard
- PySide6.QtWidgets - bootstrap da aplicacao desktop
- PySide6.QtGui - configuracao de fonte padrao

Fluxo geral:
1) Cria a instancia de QApplication.
2) Define nome, estilo e fonte padrao da aplicacao.
3) Instancia a janela principal e inicia o loop do Qt.

Estrutura interna:
Metodos principais:
- principal(): ponto de entrada executavel do desktop.
[DOC-FILE-END]==============================================================="""

import sys

import config
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication

from src.infraestrutura.caminhos import resolver_caminho_recurso
from src.ui.ui_main import JanelaPainelAutomacao


def _resolver_caminho_icone() -> str:
    candidatos = [
        resolver_caminho_recurso("public", "app-icon.ico"),
        resolver_caminho_recurso("public", "app-icon.png"),
    ]
    for caminho in candidatos:
        if caminho.exists():
            return str(caminho)
    return ""


def _configurar_fonte_aplicacao(app: QApplication) -> None:
    candidatos_fonte = [
        resolver_caminho_recurso("public", "fonts", "Manrope-Variable.ttf"),
    ]

    for caminho_fonte in candidatos_fonte:
        if not caminho_fonte.exists():
            continue

        identificador = QFontDatabase.addApplicationFont(str(caminho_fonte))
        if identificador < 0:
            continue

        familias = QFontDatabase.applicationFontFamilies(identificador)
        if not familias:
            continue

        app.setFont(QFont(familias[0], 10))
        return

    for familia in ("Aptos", "Bahnschrift", "Segoe UI"):
        if QFontDatabase.hasFamily(familia):
            app.setFont(QFont(familia, 10))
            return

    app.setFont(QFont("Segoe UI", 10))


def principal() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(config.NOME_APLICACAO)
    app.setStyle("Fusion")
    _configurar_fonte_aplicacao(app)

    caminho_icone = _resolver_caminho_icone()
    if caminho_icone:
        icone = QIcon(caminho_icone)
        app.setWindowIcon(icone)
    else:
        icone = QIcon()

    janela = JanelaPainelAutomacao()
    if not icone.isNull():
        janela.setWindowIcon(icone)
    janela.showMaximized()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(principal())
