"""==[DOC-FILE]===============================================================
Arquivo : src/servicos/reajustador_taxas.py
Classe  : ReajustadorTaxas (class)
Pacote  : src.servicos
Modulo  : Servicos - Reajuste por Linha

Papel   : Executa o fluxo completo de reajuste em uma unica linha da tabela,
          respeitando a sequencia oficial do processo descrito no fluxo.

Conecta com:
- config - valor do reajuste e rotulos das acoes
- src.infraestrutura.acoes_navegador - cliques e interacoes com o DOM
- src.paginas.pagina_tabelas_cliente - espera do modal e retorno a tabela

Fluxo geral:
1) Abre o menu da linha e clica em `Reajuste`.
2) Marca `Considerar todos os trechos`.
3) Seleciona `% Taxas adm.`, marca `Valor fixo` e preenche o valor.
4) Adiciona, salva e confirma o SweetAlert com `Sim`.

Estrutura interna:
Metodos principais:
- processar_linha(): executa o reajuste completo de uma linha.
- _selecionar_taxa_administrativa(): trata o Select2 da taxa.
- _preencher_valor_reajuste(): escreve o valor configurado.
- _confirmar_popup_reajuste(): confirma o SweetAlert final.
[DOC-FILE-END]==============================================================="""

from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

import config
from src.infraestrutura.acoes_navegador import AcoesNavegador
from src.infraestrutura.rastreador_etapas import RastreadorEtapas
from src.paginas.pagina_tabelas_cliente import PaginaTabelasCliente


class ReajustadorTaxas:
    def __init__(
        self,
        acoes_navegador: AcoesNavegador,
        pagina_tabelas_cliente: PaginaTabelasCliente,
        valor_reajuste: float,
        rastreador: Optional[RastreadorEtapas] = None,
    ) -> None:
        self.acoes_navegador = acoes_navegador
        self.pagina_tabelas_cliente = pagina_tabelas_cliente
        self.valor_reajuste = valor_reajuste
        self.rastreador = rastreador
        self._contexto_linha: Dict[str, Any] = {}

    def processar_linha(self, linha: WebElement, contexto: Optional[Dict[str, Any]] = None) -> None:
        self._contexto_linha = contexto or {}

        with self._etapa("abrir_menu_acoes", "Abrindo menu de acoes da linha"):
            self._abrir_menu_acoes_linha(linha)

        with self._etapa("clicar_reajuste", "Clicando em Reajuste no menu"):
            self.acoes_navegador.clicar_por_texto(config.ROTULOS_REAJUSTE["reajuste"])

        with self._etapa("aguardar_modal_reajuste", "Aguardando modal de reajuste abrir"):
            modal = self.pagina_tabelas_cliente.aguardar_modal_reajuste()

        with self._etapa("marcar_considerar_trechos", "Marcando Considerar todos os trechos"):
            self._marcar_considerar_todos_trechos(modal)

        with self._etapa("selecionar_taxa_administrativa", "Selecionando % Taxas adm. no Select2"):
            self._selecionar_taxa_administrativa(modal)

        with self._etapa("marcar_valor_fixo", "Marcando tipo Valor fixo"):
            self._marcar_tipo_valor_fixo(modal)

        with self._etapa("preencher_valor_reajuste", f"Preenchendo valor {self.valor_reajuste}"):
            self._preencher_valor_reajuste(modal)

        with self._etapa("clicar_adicionar", "Clicando em Adicionar"):
            self._clicar_botao_adicionar(modal)

        with self._etapa("clicar_salvar", "Clicando em Salvar"):
            self._clicar_botao_salvar(modal)

        with self._etapa("confirmar_popup_reajuste", "Confirmando popup SweetAlert"):
            self._confirmar_popup_reajuste(modal)

        with self._etapa("aguardar_modal_fechar", "Aguardando modal fechar"):
            self.pagina_tabelas_cliente.aguardar_modal_fechar()

    def _abrir_menu_acoes_linha(self, linha: WebElement) -> None:
        botao_menu = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "botao_menu_linha", contexto=linha
        )
        if botao_menu is None:
            raise NoSuchElementException("Botao de menu da linha nao encontrado.")

        self.acoes_navegador.clicar_com_seguranca(botao_menu)
        self.acoes_navegador.aguardar_carregamento_finalizar(timeout=5)

    def _marcar_considerar_todos_trechos(self, modal: WebElement) -> None:
        botao = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "checkbox_considerar_trechos", contexto=modal
        ) or self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "checkbox_considerar_trechos"
        )
        if botao is None:
            raise NoSuchElementException(
                "Botao 'Considerar todos os trechos' nao encontrado."
            )

        icone_checkbox = self._obter_icone_considerar_trechos(botao)
        if self._todos_trechos_selecionados(icone_checkbox):
            return

        alvo_clique = icone_checkbox or botao
        self.acoes_navegador.clicar_com_seguranca(alvo_clique)

        try:
            WebDriverWait(self.acoes_navegador.navegador, 10).until(
                lambda _driver: self._todos_trechos_selecionados(
                    self._obter_icone_considerar_trechos(
                        self.acoes_navegador.buscar_primeiro_por_nome_seletor(
                            "checkbox_considerar_trechos", contexto=modal
                        )
                        or self.acoes_navegador.buscar_primeiro_por_nome_seletor(
                            "checkbox_considerar_trechos"
                        )
                    )
                )
            )
        except TimeoutException:
            raise TimeoutException(
                "Selecao de 'Considerar todos os trechos' nao foi confirmada."
            )

    def _selecionar_taxa_administrativa(self, modal: WebElement) -> None:
        campo_taxa = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "campo_taxa_reajuste", contexto=modal
        ) or self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "campo_taxa_reajuste"
        )
        if campo_taxa is None:
            raise NoSuchElementException("Campo de taxa do reajuste nao encontrado.")

        self.acoes_navegador.clicar_com_seguranca(
            self.acoes_navegador.resolver_alvo_clicavel(campo_taxa) or campo_taxa
        )
        self.acoes_navegador.selecionar_opcao_select2(
            config.ROTULOS_REAJUSTE["taxa_alvo"]
        )

    def _marcar_tipo_valor_fixo(self, modal: WebElement) -> None:
        radio_valor_fixo = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "radio_valor_fixo", contexto=modal
        ) or self.acoes_navegador.buscar_primeiro_por_nome_seletor("radio_valor_fixo")
        if radio_valor_fixo is None:
            raise NoSuchElementException("Opcao 'Valor fixo' nao encontrada.")

        if radio_valor_fixo.tag_name.lower() == "input":
            if radio_valor_fixo.is_selected():
                return
            self.acoes_navegador.clicar_com_seguranca(radio_valor_fixo)
            return

        self.acoes_navegador.clicar_com_seguranca(radio_valor_fixo)

    def _preencher_valor_reajuste(self, modal: WebElement) -> None:
        campo_valor = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "campo_valor_reajuste", contexto=modal
        ) or self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "campo_valor_reajuste"
        )
        if campo_valor is None:
            raise NoSuchElementException("Campo de valor do reajuste nao encontrado.")

        self.acoes_navegador.limpar_e_digitar(
            campo_valor, self._formatar_valor_reajuste(self.valor_reajuste)
        )

    def _clicar_botao_adicionar(self, modal: WebElement) -> None:
        botao_adicionar = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "botao_adicionar", contexto=modal
        ) or self.acoes_navegador.buscar_primeiro_por_nome_seletor("botao_adicionar")
        if botao_adicionar is None:
            raise NoSuchElementException("Botao 'Adicionar' nao encontrado.")

        self.acoes_navegador.clicar_com_seguranca(botao_adicionar)
        self.acoes_navegador.aguardar_carregamento_finalizar(timeout=5)

    def _clicar_botao_salvar(self, modal: WebElement) -> None:
        botao_salvar = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "botao_salvar", contexto=modal
        ) or self.acoes_navegador.buscar_primeiro_por_nome_seletor("botao_salvar")
        if botao_salvar is None:
            raise NoSuchElementException("Botao 'Salvar' nao encontrado.")

        self.acoes_navegador.clicar_com_seguranca(botao_salvar)

    def _confirmar_popup_reajuste(self, modal: WebElement) -> None:
        if not config.CONFIRMAR_REAJUSTE_FINAL:
            botao_cancelar = self.acoes_navegador.aguardar_seletor(
                "botao_cancelar_swal", condicao="clicavel", timeout=10
            )
            self.acoes_navegador.clicar_com_seguranca(botao_cancelar)
            self._aguardar_popup_swal_fechar()
            self._fechar_modal_sem_salvar(modal)
            return

        botao_confirmar = self.acoes_navegador.aguardar_seletor(
            "botao_confirmar_swal", condicao="clicavel", timeout=10
        )
        self.acoes_navegador.clicar_com_seguranca(botao_confirmar)
        self._aguardar_primeiro_swal_fechar()
        self.acoes_navegador.aguardar_carregamento_finalizar()
        self._clicar_ok_popup_sucesso()
        self._aguardar_popup_swal_fechar()
        self.acoes_navegador.aguardar_carregamento_finalizar()
        self._fechar_modal_apos_reajuste(modal)

    def _aguardar_primeiro_swal_fechar(self) -> None:
        try:
            WebDriverWait(self.acoes_navegador.navegador, 10).until(
                lambda _driver: self.acoes_navegador.buscar_primeiro_por_nome_seletor(
                    "botao_cancelar_swal"
                )
                is None
            )
        except TimeoutException:
            pass

    def _clicar_ok_popup_sucesso(self) -> None:
        try:
            botao_ok = self.acoes_navegador.aguardar_seletor(
                "botao_confirmar_swal", condicao="clicavel", timeout=10
            )
            self.acoes_navegador.clicar_com_seguranca(botao_ok)
        except TimeoutException:
            pass

    def _fechar_modal_apos_reajuste(self, modal: WebElement) -> None:
        botao_fechar = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
            "botao_fechar_modal", contexto=modal
        ) or self.acoes_navegador.buscar_primeiro_por_nome_seletor("botao_fechar_modal")
        if botao_fechar is not None:
            self.acoes_navegador.clicar_com_seguranca(botao_fechar)
            self.acoes_navegador.aguardar_carregamento_finalizar(timeout=5)
            return
        try:
            self.acoes_navegador.clicar_por_texto(
                config.ROTULOS_REAJUSTE["fechar"], contexto=modal, timeout=5
            )
        except TimeoutException:
            pass
        self.acoes_navegador.aguardar_carregamento_finalizar(timeout=5)

    def _aguardar_popup_swal_fechar(self) -> None:
        try:
            WebDriverWait(self.acoes_navegador.navegador, 10).until(
                lambda _driver: self.acoes_navegador.buscar_primeiro_por_nome_seletor(
                    "botao_confirmar_swal"
                )
                is None
                and self.acoes_navegador.buscar_primeiro_por_nome_seletor(
                    "botao_cancelar_swal"
                )
                is None
            )
        except TimeoutException:
            self.acoes_navegador.aguardar_carregamento_finalizar(timeout=5)

    def _fechar_modal_sem_salvar(self, modal: WebElement) -> None:
        try:
            self.acoes_navegador.clicar_por_texto(
                config.ROTULOS_REAJUSTE["fechar"], contexto=modal, timeout=5
            )
        except TimeoutException:
            botao_fechar = self.acoes_navegador.buscar_primeiro_por_nome_seletor(
                "botao_fechar_modal", contexto=modal
            ) or self.acoes_navegador.buscar_primeiro_por_nome_seletor(
                "botao_fechar_modal"
            )
            if botao_fechar is None:
                raise NoSuchElementException(
                    "Botao para fechar o modal de reajuste nao encontrado."
                )
            self.acoes_navegador.clicar_com_seguranca(botao_fechar)

        self.acoes_navegador.aguardar_carregamento_finalizar(timeout=5)

    @staticmethod
    def _obter_icone_considerar_trechos(botao: Optional[WebElement]) -> Optional[WebElement]:
        if botao is None:
            return None

        icones = botao.find_elements(
            By.XPATH,
            ".//i[contains(@class, 'fa-square') or contains(@class, 'fa-check-square')]",
        )
        return icones[0] if icones else None

    @staticmethod
    def _todos_trechos_selecionados(icone_checkbox: Optional[WebElement]) -> bool:
        if icone_checkbox is None:
            return False
        return "fa-check-square" in (icone_checkbox.get_attribute("class") or "").lower()

    def _etapa(self, nome: str, descricao: str):
        if self.rastreador:
            return self.rastreador.etapa(nome, descricao, self._contexto_linha)
        return _contexto_nulo()

    @staticmethod
    def _formatar_valor_reajuste(valor: float) -> str:
        valor_texto = f"{valor:.2f}"
        if valor_texto.endswith("00"):
            return str(int(valor))
        return valor_texto.rstrip("0").rstrip(".")


@contextmanager
def _contexto_nulo() -> Generator[None, None, None]:
    yield
