"""==[DOC-FILE]===============================================================
Arquivo : src/infraestrutura/fabrica_navegador.py
Classe  : FabricaNavegador (class)
Pacote  : src.infraestrutura
Modulo  : Infraestrutura - Bootstrap do Navegador

Papel   : Centraliza a criacao do navegador com as opcoes necessarias para a
          automacao, priorizando Chrome e caindo para Edge quando necessario.

Conecta com:
- config - flags de headless e timeout de carregamento
- selenium.webdriver - instancia concreta do navegador

Fluxo geral:
1) Monta as opcoes padronizadas do navegador.
2) Aplica configuracoes de headless quando necessario.
3) Tenta iniciar Chrome e, em caso de falha, usa Edge como fallback.

Estrutura interna:
Metodos principais:
- criar(): instancia o navegador com as opcoes padronizadas do projeto.
[DOC-FILE-END]==============================================================="""

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ChromeOptions, EdgeOptions
from selenium.webdriver.chrome.service import Service as ServicoChrome
from selenium.webdriver.edge.service import Service as ServicoEdge
from selenium.webdriver.remote.webdriver import WebDriver

import config


class FabricaNavegador:
    def criar(self) -> WebDriver:
        ultimo_erro: Exception | None = None

        for fabrica in (
            self._criar_chrome,
            self._criar_edge,
        ):
            try:
                navegador = fabrica()
                navegador.set_page_load_timeout(config.TEMPO_MAXIMO_CARREGAMENTO)
                return navegador
            except WebDriverException as erro:
                ultimo_erro = erro

        raise RuntimeError(
            "Nao foi possivel iniciar um navegador suportado. Verifique Chrome ou Edge."
        ) from ultimo_erro

    def _criar_chrome(self) -> WebDriver:
        opcoes = ChromeOptions()
        self._configurar_argumentos_padrao(opcoes)
        return webdriver.Chrome(service=ServicoChrome(), options=opcoes)

    def _criar_edge(self) -> WebDriver:
        opcoes = EdgeOptions()
        self._configurar_argumentos_padrao(opcoes)
        return webdriver.Edge(service=ServicoEdge(), options=opcoes)

    @staticmethod
    def _configurar_argumentos_padrao(opcoes: ChromeOptions | EdgeOptions) -> None:
        opcoes.add_argument("--start-maximized")
        opcoes.add_argument("--disable-notifications")
        opcoes.add_argument("--disable-infobars")
        opcoes.add_argument("--disable-dev-shm-usage")
        opcoes.add_argument("--no-sandbox")

        if config.MODO_HEADLESS:
            opcoes.add_argument("--headless=new")
            opcoes.add_argument("--window-size=1600,1000")
