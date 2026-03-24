"""==[DOC-FILE]===============================================================
Arquivo : src/infraestrutura/acoes_navegador.py
Classe  : AcoesNavegador (class)
Pacote  : src.infraestrutura
Modulo  : Infraestrutura - Utilitarios Selenium

Papel   : Encapsula operacoes repetitivas de Selenium, como esperar, localizar,
          clicar com seguranca e interagir com Select2 sem espalhar detalhes
          de infraestrutura pelas regras de negocio.

Conecta com:
- config - seletores e timeouts centralizados
- selenium.webdriver - navegador, waits e elementos web
- src.paginas e src.servicos - consumidores dos utilitarios

Fluxo geral:
1) Resolve seletores por nome, em vez de espalhar XPaths no codigo.
2) Aguarda elementos ficarem presentes, visiveis ou clicaveis.
3) Executa cliques seguros, digitacao controlada e selecao no Select2.

Estrutura interna:
Metodos principais:
- aguardar_seletor(): resolve um seletor nomeado com espera explicita.
- clicar_por_texto(): encontra e clica em um texto clicavel.
- selecionar_opcao_select2(): trata dropdowns dinamicos do ESL Cloud.
- clicar_com_seguranca(): scrolla e tenta click nativo com fallback em JavaScript.
[DOC-FILE-END]==============================================================="""

import logging
import re
from typing import List, Optional

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    JavascriptException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as condicoes_esperadas
from selenium.webdriver.support.ui import WebDriverWait

import config
from src.infraestrutura.debug_visual import DebugVisualClique


class AcoesNavegador:
    MAPA_BY = {
        "css selector": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "id": By.ID,
        "name": By.NAME,
        "class name": By.CLASS_NAME,
        "tag name": By.TAG_NAME,
        "link text": By.LINK_TEXT,
        "partial link text": By.PARTIAL_LINK_TEXT,
    }

    def __init__(self, navegador: WebDriver, registrador: logging.Logger) -> None:
        self.navegador = navegador
        self.registrador = registrador
        self.espera = WebDriverWait(self.navegador, config.TEMPO_ESPERA_PADRAO)
        self.debug_visual = DebugVisualClique(navegador, registrador)

    def aguardar_documento_pronto(self) -> None:
        WebDriverWait(self.navegador, config.TEMPO_MAXIMO_CARREGAMENTO).until(
            lambda navegador: navegador.execute_script("return document.readyState")
            == "complete"
        )

    def aguardar_carregamento_finalizar(self, timeout: int = 15) -> None:
        def sem_camadas_carregando(navegador: WebDriver) -> bool:
            for tipo_by, seletor in config.SELETORES.get("camada_carregamento", []):
                elementos = navegador.find_elements(self.MAPA_BY[tipo_by], seletor)
                for elemento in elementos:
                    try:
                        if elemento.is_displayed():
                            return False
                    except StaleElementReferenceException:
                        continue
            return True

        try:
            WebDriverWait(self.navegador, timeout).until(sem_camadas_carregando)
        except TimeoutException:
            self.registrador.info(
                "Continuando execucao apos timeout aguardando camadas de carregamento."
            )

    def aguardar_seletor(
        self,
        nome_seletor: str,
        condicao: str,
        timeout: Optional[int] = None,
        contexto: Optional[WebElement] = None,
    ) -> WebElement:
        tempo_espera = timeout or config.TEMPO_ESPERA_PADRAO
        raiz_busca = contexto or self.navegador

        def localizar(_driver: WebDriver):
            try:
                for elemento in self.buscar_todos_por_nome_seletor(
                    nome_seletor, contexto=raiz_busca
                ):
                    if condicao == "clicavel":
                        alvo_clicavel = self.resolver_alvo_clicavel(elemento)
                        if alvo_clicavel and self.elemento_clicavel(alvo_clicavel):
                            return alvo_clicavel
                        continue
                    if condicao == "visivel":
                        if self.elemento_visivel(elemento):
                            return elemento
                        continue
                    return elemento
            except StaleElementReferenceException:
                return False
            return False

        try:
            return WebDriverWait(self.navegador, tempo_espera).until(localizar)
        except TimeoutException as erro:
            raise TimeoutException(
                f"Falha ao localizar seletor '{nome_seletor}' com condicao '{condicao}'."
            ) from erro

    def buscar_primeiro_por_nome_seletor(
        self, nome_seletor: str, contexto: Optional[WebElement] = None
    ) -> Optional[WebElement]:
        for elemento in self.buscar_todos_por_nome_seletor(
            nome_seletor, contexto=contexto
        ):
            if self.elemento_visivel(elemento):
                return elemento
        return None

    def buscar_todos_por_nome_seletor(
        self, nome_seletor: str, contexto: Optional[WebElement] = None
    ) -> List[WebElement]:
        raiz_busca = contexto or self.navegador
        elementos_encontrados: List[WebElement] = []
        elementos_vistos: set[str] = set()
        for tipo_by, seletor in config.SELETORES.get(nome_seletor, []):
            for elemento in raiz_busca.find_elements(self.MAPA_BY[tipo_by], seletor):
                chave_elemento = getattr(elemento, "id", "")
                if chave_elemento in elementos_vistos:
                    continue
                elementos_vistos.add(chave_elemento)
                elementos_encontrados.append(elemento)
        return elementos_encontrados

    def clicar_por_texto(
        self,
        texto: str,
        contexto: Optional[WebElement] = None,
        timeout: Optional[int] = None,
    ) -> None:
        elemento = self.buscar_elemento_clicavel_por_texto(texto, contexto=contexto)
        if elemento is None and timeout:
            WebDriverWait(self.navegador, timeout).until(
                lambda _driver: self.buscar_elemento_clicavel_por_texto(
                    texto, contexto=contexto
                )
                is not None
            )
            elemento = self.buscar_elemento_clicavel_por_texto(texto, contexto=contexto)

        if elemento is None:
            raise TimeoutException(
                f"Elemento clicavel com texto '{texto}' nao encontrado."
            )

        self.clicar_com_seguranca(elemento)

    def buscar_elemento_clicavel_por_texto(
        self, texto: str, contexto: Optional[WebElement] = None
    ) -> Optional[WebElement]:
        literal = self.literal_xpath(texto)
        expressoes = [
            f".//*[self::button or self::a or self::span or self::div or self::li][normalize-space()={literal}]",
            f".//*[normalize-space()={literal}]/ancestor-or-self::*[self::button or self::a or @role='button' or self::li][1]",
            f".//*[contains(normalize-space(), {literal})]/ancestor-or-self::*[self::button or self::a or @role='button' or self::li][1]",
        ]

        raiz_busca = contexto or self.navegador
        for expressao in expressoes:
            elementos = raiz_busca.find_elements(By.XPATH, expressao)
            for elemento in elementos:
                alvo_clicavel = self.resolver_alvo_clicavel(elemento)
                if alvo_clicavel and self.elemento_clicavel(alvo_clicavel):
                    return alvo_clicavel
        return None

    def selecionar_opcao_select2(self, texto_opcao: str) -> None:
        literal = self.literal_xpath(texto_opcao)
        expressoes = [
            f"//li[contains(@class, 'select2-results__option') and normalize-space()={literal}]",
            f"//*[contains(@class, 'select2-results__option') and contains(normalize-space(), {literal})]",
            f"//*[normalize-space()={literal}]",
        ]

        ultimo_erro: Optional[Exception] = None
        for expressao in expressoes:
            try:
                elemento = WebDriverWait(self.navegador, 10).until(
                    condicoes_esperadas.element_to_be_clickable((By.XPATH, expressao))
                )
                self.clicar_com_seguranca(elemento)
                self.aguardar_carregamento_finalizar(timeout=5)
                return
            except TimeoutException as erro:
                ultimo_erro = erro

        raise TimeoutException(
            f"Opcao '{texto_opcao}' nao localizada no componente Select2."
        ) from ultimo_erro

    def resolver_alvo_clicavel(self, elemento: WebElement) -> Optional[WebElement]:
        if self.elemento_clicavel(elemento):
            return elemento

        try:
            ancestrais = elemento.find_elements(
                By.XPATH,
                "./ancestor-or-self::*[self::button or self::a or @role='button' or self::label]",
            )
        except StaleElementReferenceException:
            return None

        for ancestral in ancestrais:
            if self.elemento_clicavel(ancestral):
                return ancestral

        return elemento if self.elemento_visivel(elemento) else None

    def elemento_clicavel(self, elemento: WebElement) -> bool:
        try:
            if not self.elemento_visivel(elemento):
                return False
            if not elemento.is_enabled():
                return False

            atributo_disabled = (elemento.get_attribute("disabled") or "").lower()
            aria_disabled = (elemento.get_attribute("aria-disabled") or "").lower()
            classes = (elemento.get_attribute("class") or "").lower()
            return (
                atributo_disabled not in {"true", "disabled"}
                and aria_disabled != "true"
                and "disabled" not in classes
            )
        except StaleElementReferenceException:
            return False

    def clicar_com_seguranca(self, elemento: WebElement) -> None:
        try:
            self.navegador.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                elemento,
            )
        except JavascriptException:
            pass

        self.debug_visual.destacar_antes_do_clique(elemento)

        try:
            elemento.click()
            return
        except (ElementClickInterceptedException, WebDriverException):
            self.navegador.execute_script("arguments[0].click();", elemento)

    def limpar_e_digitar(self, elemento: WebElement, valor: str) -> None:
        self.debug_visual.destacar_antes_da_digitacao(elemento, valor)
        elemento.click()
        elemento.send_keys(Keys.CONTROL, "a")
        elemento.send_keys(Keys.BACKSPACE)
        if valor:
            elemento.send_keys(valor)
        self.debug_visual.remover_destaque(elemento)

    @staticmethod
    def texto_seguro(elemento: WebElement) -> str:
        try:
            return elemento.text or ""
        except StaleElementReferenceException:
            return ""

    @staticmethod
    def elemento_visivel(elemento: WebElement) -> bool:
        try:
            return elemento.is_displayed()
        except StaleElementReferenceException:
            return False

    @staticmethod
    def normalizar_espacos(texto: str) -> str:
        return re.sub(r"\s+", " ", texto or "").strip()

    @staticmethod
    def literal_xpath(texto: str) -> str:
        if "'" not in texto:
            return f"'{texto}'"
        if '"' not in texto:
            return f'"{texto}"'

        partes = texto.split("'")
        texto_unido = ", \"'\", ".join(f"'{parte}'" for parte in partes)
        return f"concat({texto_unido})"
