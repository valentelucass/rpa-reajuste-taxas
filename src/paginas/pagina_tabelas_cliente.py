"""==[DOC-FILE]===============================================================
Arquivo : src/paginas/pagina_tabelas_cliente.py
Classe  : PaginaTabelasCliente (class)
Pacote  : src.paginas
Modulo  : Paginas - Tabelas de Cliente

Papel   : Encapsula a navegacao pelo menu, aplicacao dos filtros iniciais,
          leitura da tabela, deteccao de total de registros e paginacao.

Conecta com:
- config - textos do menu, filtros e seletores
- src.infraestrutura.acoes_navegador - utilitarios Selenium reutilizados
- src.servicos - consumo das linhas e do modal de reajuste

Fluxo geral:
1) Navega por `Cadastros > Tabelas de preco > Tabelas de cliente`.
2) Limpa a filial responsavel, marca `Ativa = Sim` e pesquisa.
3) Fornece as linhas visiveis da pagina atual e controla a paginacao.

Estrutura interna:
Metodos principais:
- preparar_filtros_iniciais(): aplica exatamente o fluxo definido em `docs/fluxo.md`.
- obter_linhas_tabela(): retorna todas as linhas `.vue-item` visiveis.
- obter_total_registros(): interpreta `Exibindo X - Y de Z`.
- ir_para_proxima_pagina(): avanca enquanto existir o botao `fa-angle-right`.
[DOC-FILE-END]==============================================================="""

import re
from typing import List, Optional, Tuple

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

import config
from src.infraestrutura.acoes_navegador import AcoesNavegador


class PaginaTabelasCliente:
    def __init__(self, acoes_navegador: AcoesNavegador) -> None:
        self.acoes_navegador = acoes_navegador

    def acessar(self) -> None:
        for nome_menu in config.CAMINHO_MENUS:
            self.acoes_navegador.clicar_por_texto(nome_menu)
            self.acoes_navegador.aguardar_carregamento_finalizar()

    def preparar_filtros_iniciais(self) -> None:
        self.limpar_filial_responsavel()
        self.selecionar_filtro_ativa()
        self.clicar_botao_pesquisar()
        self.aguardar_resultados_pesquisa()

    def limpar_filial_responsavel(self) -> None:
        botao_limpar = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "limpar_filial_responsavel"
        )
        if botao_limpar is not None and self.acoes_navegador.elemento_visivel(
            botao_limpar
        ):
            self.acoes_navegador.clicar_com_seguranca(botao_limpar)
            self.acoes_navegador.aguardar_carregamento_finalizar(timeout=5)
            return

        campo_filial = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "campo_filial_responsavel"
        )
        if campo_filial is None:
            raise NoSuchElementException("Campo 'Filial Responsavel' nao encontrado.")

        self.acoes_navegador.clicar_com_seguranca(campo_filial)
        botao_limpar = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "limpar_filial_responsavel"
        )
        if botao_limpar is None:
            return

        self.acoes_navegador.clicar_com_seguranca(botao_limpar)
        self.acoes_navegador.aguardar_carregamento_finalizar(timeout=5)

    def selecionar_filtro_ativa(self) -> None:
        campo_ativa = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "campo_ativa"
        )
        if campo_ativa is None:
            raise NoSuchElementException("Campo 'Ativa' nao encontrado.")

        self.acoes_navegador.clicar_com_seguranca(campo_ativa)
        self.acoes_navegador.selecionar_opcao_select2(
            config.ROTULOS_FILTROS["ativa_sim"]
        )

    def clicar_botao_pesquisar(self) -> None:
        self.acoes_navegador.aguardar_carregamento_finalizar()
        botao_pesquisar = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "botao_pesquisar"
        )
        if botao_pesquisar is None:
            botao_pesquisar = self.acoes_navegador.aguardar_seletor(
                "botao_pesquisar", condicao="clicavel"
            )
        self.acoes_navegador.clicar_com_seguranca(botao_pesquisar)

    def aguardar_resultados_pesquisa(self) -> None:
        self.acoes_navegador.aguardar_carregamento_finalizar()
        self.acoes_navegador.espera.until(
            lambda _driver: self.acoes_navegador.buscar_primeiro_por_nome_seletor(
                "modal_reajuste"
            )
            is None
            and (
                bool(self.obter_linhas_tabela(aguardar_presenca=False))
                or self.esta_sem_resultados()
            )
        )
        self.acoes_navegador.espera.until(
            lambda _driver: bool(self.obter_linhas_tabela(aguardar_presenca=False))
            or self.esta_sem_resultados()
        )

    def obter_linhas_tabela(self, aguardar_presenca: bool) -> List[WebElement]:
        if aguardar_presenca:
            self.acoes_navegador.aguardar_carregamento_finalizar()
            try:
                WebDriverWait(self.acoes_navegador.navegador, 15).until(
                    lambda _driver: bool(
                        self.acoes_navegador.buscar_todos_por_nome_seletor(
                            "linhas_tabela"
                        )
                    )
                    or self.esta_sem_resultados()
                )
            except TimeoutException:
                return []

        return [
            linha
            for linha in self.acoes_navegador.buscar_todos_por_nome_seletor(
                "linhas_tabela"
            )
            if self.acoes_navegador.elemento_visivel(linha)
        ]

    def esta_sem_resultados(self) -> bool:
        html_pagina = self.acoes_navegador.navegador.page_source or ""
        return any(texto in html_pagina for texto in config.TEXTOS_SEM_RESULTADO)

    def obter_assinatura_pagina(self) -> Tuple[int, Tuple[str, ...]]:
        linhas = self.obter_linhas_tabela(aguardar_presenca=False)
        textos_referencia = tuple(
            self.acoes_navegador.normalizar_espacos(
                self.acoes_navegador.texto_seguro(linha)
            )
            for linha in linhas[:3]
        )
        return len(linhas), textos_referencia

    def obter_total_registros(self) -> int:
        informacao = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "informacao_quantidade_registros"
        )
        if informacao is None:
            return len(self.obter_linhas_tabela(aguardar_presenca=False))

        texto = self.acoes_navegador.normalizar_espacos(
            self.acoes_navegador.texto_seguro(informacao)
        )
        resultado = re.search(r"de\s+(\d+)", texto)
        if resultado:
            return int(resultado.group(1))

        return len(self.obter_linhas_tabela(aguardar_presenca=False))

    def ir_para_proxima_pagina(self) -> bool:
        botao_proxima_pagina = self.obter_botao_proxima_pagina()
        if botao_proxima_pagina is None:
            self.acoes_navegador.registrador.info(
                "Paginacao encerrada: botao de proxima pagina nao encontrado."
            )
            return False

        assinatura_anterior = self.obter_assinatura_pagina()
        self.acoes_navegador.clicar_com_seguranca(botao_proxima_pagina)

        try:
            WebDriverWait(self.acoes_navegador.navegador, 15).until(
                lambda _driver: self.obter_assinatura_pagina() != assinatura_anterior
            )
        except TimeoutException:
            self.acoes_navegador.registrador.info(
                "Paginacao encerrada: nenhuma mudanca apos clique em proxima pagina."
            )
            return False

        self.acoes_navegador.aguardar_carregamento_finalizar()
        self.aguardar_resultados_pesquisa()
        return True

    def obter_botao_proxima_pagina(self) -> Optional[WebElement]:
        for tipo_by, seletor in config.SELETORES["botao_proxima_pagina"]:
            elementos = self.acoes_navegador.navegador.find_elements(
                self.acoes_navegador.MAPA_BY[tipo_by], seletor
            )
            for elemento in elementos:
                alvo_clicavel = self.acoes_navegador.resolver_alvo_clicavel(elemento)
                if alvo_clicavel and self.acoes_navegador.elemento_clicavel(
                    alvo_clicavel
                ):
                    return alvo_clicavel
        return None

    def aguardar_modal_reajuste(self) -> WebElement:
        self.acoes_navegador.aguardar_seletor(
            "checkbox_considerar_trechos",
            condicao="visivel",
            timeout=20,
        )
        self.acoes_navegador.aguardar_seletor(
            "campo_taxa_reajuste",
            condicao="visivel",
            timeout=20,
        )
        self.acoes_navegador.aguardar_seletor(
            "botao_salvar",
            condicao="visivel",
            timeout=20,
        )
        modal = self.acoes_navegador.buscar_primeiro_por_nome_seletor("modal_reajuste")
        if modal is None:
            modal = self.acoes_navegador.aguardar_seletor(
                "modal_reajuste", condicao="visivel", timeout=20
            )
        return modal

    def aguardar_modal_fechar(self) -> None:
        try:
            WebDriverWait(self.acoes_navegador.navegador, 15).until(
                lambda _driver: self.acoes_navegador.buscar_primeiro_por_nome_seletor(
                    "modal_reajuste"
                )
                is None
            )
        except TimeoutException as erro:
            self.acoes_navegador.aguardar_carregamento_finalizar()
            if (
                self.acoes_navegador.buscar_primeiro_por_nome_seletor("modal_reajuste")
                is not None
            ):
                raise TimeoutException(
                    "Modal de reajuste permaneceu aberto apos a tentativa de fechamento."
                ) from erro
