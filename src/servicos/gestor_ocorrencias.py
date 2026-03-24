"""==[DOC-FILE]===============================================================
Arquivo : src/servicos/gestor_ocorrencias.py
Classe  : GestorOcorrenciasProcessamento (class)
Pacote  : src.servicos
Modulo  : Servicos - Tratamento de Erros e Evidencias

Papel   : Registra sucessos e falhas em CSV, gera screenshots de erro e tenta
          recuperar a interface para que a automacao continue apos falhas isoladas.

Conecta com:
- config - caminhos de logs e screenshots
- src.infraestrutura.acoes_navegador - acesso ao navegador e logger tecnico

Fluxo geral:
1) Em sucesso, grava a ocorrencia em `logs/processamento.csv`.
2) Em erro, gera screenshot, grava o CSV e tenta fechar modal/interface travada.
3) Devolve o controle para o loop principal continuar a proxima linha.

Estrutura interna:
Metodos principais:
- registrar_sucesso(): registra linha concluida.
- registrar_falha(): registra falha e evidencia visual.
- recuperar_interface_apos_erro(): tenta restabelecer a tela apos erro.
[DOC-FILE-END]==============================================================="""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys

import config
from src.infraestrutura.acoes_navegador import AcoesNavegador
from src.infraestrutura.retencao_artefatos import (
    limitar_csv_por_registros,
    manter_arquivos_mais_recentes,
)


class GestorOcorrenciasProcessamento:
    def __init__(self, acoes_navegador: AcoesNavegador) -> None:
        self.acoes_navegador = acoes_navegador

    def registrar_sucesso(
        self,
        numero_pagina: int,
        numero_linha: int,
        identificador: str,
        mensagem: str,
    ) -> None:
        self._registrar_csv(
            numero_pagina=numero_pagina,
            numero_linha=numero_linha,
            identificador=identificador,
            status="SUCESSO",
            mensagem=mensagem,
            caminho_screenshot="",
        )

    def registrar_falha(
        self,
        numero_pagina: int,
        numero_linha: int,
        identificador: str,
        mensagem: str,
    ) -> str:
        caminho_screenshot = self.gerar_screenshot_erro(numero_pagina, numero_linha)
        self._registrar_csv(
            numero_pagina=numero_pagina,
            numero_linha=numero_linha,
            identificador=identificador,
            status="ERRO",
            mensagem=mensagem,
            caminho_screenshot=str(caminho_screenshot) if caminho_screenshot else "",
        )
        return str(caminho_screenshot) if caminho_screenshot else ""

    def gerar_screenshot_erro(
        self, numero_pagina: int, numero_linha: int
    ) -> Optional[Path]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_arquivo = (
            config.DIRETORIO_SCREENSHOTS
            / f"erro_p{numero_pagina:03d}_l{numero_linha:03d}_{timestamp}.png"
        )
        try:
            self.acoes_navegador.navegador.save_screenshot(str(caminho_arquivo))
            manter_arquivos_mais_recentes(
                config.DIRETORIO_SCREENSHOTS,
                config.MAX_SCREENSHOTS_ARMAZENADOS,
                padroes=("*.png", "*.jpg", "*.jpeg"),
            )
            return caminho_arquivo
        except WebDriverException:
            self.acoes_navegador.registrador.error(
                "Falha ao gerar screenshot em %s", caminho_arquivo
            )
            return None

    def recuperar_interface_apos_erro(self) -> None:
        botao_fechar = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "botao_fechar_modal"
        )
        if botao_fechar is not None:
            try:
                self.acoes_navegador.clicar_com_seguranca(botao_fechar)
            except WebDriverException:
                pass

        try:
            self.acoes_navegador.navegador.switch_to.active_element.send_keys(
                Keys.ESCAPE
            )
        except WebDriverException:
            pass

        self.acoes_navegador.aguardar_carregamento_finalizar(timeout=5)

    def _registrar_csv(
        self,
        numero_pagina: int,
        numero_linha: int,
        identificador: str,
        status: str,
        mensagem: str,
        caminho_screenshot: str,
    ) -> None:
        with config.ARQUIVO_LOG_PROCESSAMENTO.open(
            "a", newline="", encoding="utf-8"
        ) as arquivo_csv:
            escritor = csv.writer(arquivo_csv, delimiter=";")
            escritor.writerow(
                [
                    datetime.now().isoformat(timespec="seconds"),
                    numero_pagina,
                    numero_linha,
                    identificador,
                    status,
                    mensagem,
                    caminho_screenshot,
                ]
            )
        limitar_csv_por_registros(
            config.ARQUIVO_LOG_PROCESSAMENTO,
            config.MAX_REGISTROS_PROCESSAMENTO,
        )
