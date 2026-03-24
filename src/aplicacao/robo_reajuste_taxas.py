"""==[DOC-FILE]===============================================================
Arquivo : src/aplicacao/robo_reajuste_taxas.py
Classe  : AutomacaoReajusteTaxas, RoboReajusteTaxas
Pacote  : src.aplicacao
Modulo  : Aplicacao - Orquestracao da Automacao

Papel   : Orquestra o fluxo completo do robo, desde o login ate o processamento
          de todas as paginas e o encerramento seguro do navegador.

Conecta com:
- config - configuracoes editaveis e seletores centralizados
- src.paginas - fluxo de login, filtros e tabela de cliente
- src.servicos - reajuste, processamento e tratamento de ocorrencias
- src.monitoramento.observador_execucao - monitoramento do progresso do robo

Fluxo geral:
1) Valida configuracao obrigatoria vinda do `.env`.
2) Prepara navegador, logger, paginas e servicos.
3) Executa login, navegacao, filtros e loop completo de paginas.
4) Permite reprocessar um unico registro com o mesmo fluxo base.

Estrutura interna:
Metodos principais:
- executar(): roda a automacao completa.
- reprocessar_registro(): roda somente um item previamente identificado.
- encerrar(): fecha o navegador com seguranca.
- _criar_componentes_execucao(): monta toda a arvore de dependencias.
[DOC-FILE-END]==============================================================="""

import config
from src.infraestrutura.acoes_navegador import AcoesNavegador
from src.infraestrutura.arquivos_execucao import PreparadorArquivosExecucao
from src.infraestrutura.fabrica_navegador import FabricaNavegador
from src.infraestrutura.rastreador_etapas import RastreadorEtapas
from src.infraestrutura.registrador_execucao import FabricaRegistradorExecucao
from src.monitoramento.observador_execucao import (
    ContextoLinhaExecucao,
    ContratoObservadorExecucao,
    ExecucaoInterrompida,
    ObservadorExecucaoVazio,
)
from src.paginas.pagina_login import PaginaLogin
from src.paginas.pagina_tabelas_cliente import PaginaTabelasCliente
from src.servicos.gestor_ocorrencias import GestorOcorrenciasProcessamento
from src.servicos.processador_tabela_clientes import ProcessadorTabelaClientes
from src.servicos.reajustador_taxas import ReajustadorTaxas


class AutomacaoReajusteTaxas:
    def __init__(
        self,
        valor_reajuste: float,
        observador_execucao: ContratoObservadorExecucao | None = None,
    ) -> None:
        self.valor_reajuste = valor_reajuste
        self.navegador = None
        self.registrador = None
        self.rastreador: RastreadorEtapas | None = None
        self.observador_execucao = observador_execucao or ObservadorExecucaoVazio()

    def executar(self) -> int:
        config.recarregar_configuracoes(sobrescrever_env=True)
        self._validar_configuracao()
        pagina_login, pagina_tabelas_cliente, processador_tabela = (
            self._criar_componentes_execucao()
        )

        try:
            self.rastreador.reiniciar_sessao()
            self.observador_execucao.registrar_mensagem_sistema(
                "Executando", "Automacao iniciada."
            )

            with self.rastreador.etapa("abrir_pagina_login", "Abrindo pagina de login"):
                pagina_login.abrir()

            with self.rastreador.etapa("fazer_login", "Autenticando na plataforma ESL Cloud"):
                pagina_login.fazer_login()

            with self.rastreador.etapa("acessar_tabelas_cliente", "Navegando ate Tabelas de Cliente"):
                pagina_tabelas_cliente.acessar()

            with self.rastreador.etapa("preparar_filtros", "Aplicando filtros iniciais (Ativa=Sim)"):
                pagina_tabelas_cliente.preparar_filtros_iniciais()

            with self.rastreador.etapa("obter_total_registros", "Lendo total de registros da tabela"):
                total_registros = pagina_tabelas_cliente.obter_total_registros()
                self.observador_execucao.definir_total_registros(total_registros)

            with self.rastreador.etapa(
                "processar_todas_paginas",
                "Processando todas as paginas da tabela",
                {"total_registros": total_registros},
            ):
                total_processado = processador_tabela.processar_todas_paginas()

            self.registrador.info(
                "Execucao finalizada. Registros tratados: %s", total_processado
            )
            self.observador_execucao.registrar_mensagem_sistema(
                "Parado", "Execucao concluida."
            )
            return total_processado
        except ExecucaoInterrompida:
            self.observador_execucao.registrar_mensagem_sistema(
                "Parado", "Execucao interrompida pelo usuario."
            )
            raise
        except Exception:
            self.registrador.exception("Falha critica na execucao principal.")
            raise

    def reprocessar_registro(self, contexto_linha: ContextoLinhaExecucao) -> bool:
        config.recarregar_configuracoes(sobrescrever_env=True)
        self._validar_configuracao()
        pagina_login, pagina_tabelas_cliente, processador_tabela = (
            self._criar_componentes_execucao()
        )
        contexto_rastreio = {
            "identificador": contexto_linha.identificador,
            "cliente": contexto_linha.cliente,
        }

        try:
            self.rastreador.reiniciar_sessao()
            self.observador_execucao.registrar_mensagem_sistema(
                "Executando",
                f"Reprocessando registro {contexto_linha.identificador}.",
            )

            with self.rastreador.etapa("reprocessar_login", "Login para reprocessamento", contexto_rastreio):
                pagina_login.abrir()
                pagina_login.fazer_login()

            with self.rastreador.etapa("reprocessar_navegacao", "Navegando ate tabelas", contexto_rastreio):
                pagina_tabelas_cliente.acessar()
                pagina_tabelas_cliente.preparar_filtros_iniciais()

            self.observador_execucao.definir_total_registros(1)

            with self.rastreador.etapa("reprocessar_registro", "Reprocessando registro especifico", contexto_rastreio):
                processador_tabela.reprocessar_registro(contexto_linha)

            self.observador_execucao.registrar_mensagem_sistema(
                "Parado", "Reprocessamento concluido."
            )
            return True
        except ExecucaoInterrompida:
            self.observador_execucao.registrar_mensagem_sistema(
                "Parado", "Reprocessamento interrompido pelo usuario."
            )
            raise
        except Exception:
            self.registrador.exception("Falha critica no reprocessamento.")
            raise

    def encerrar(self) -> None:
        if self.navegador:
            self.navegador.quit()
            self.navegador = None

    def _criar_componentes_execucao(self) -> tuple[
        PaginaLogin, PaginaTabelasCliente, ProcessadorTabelaClientes
    ]:
        PreparadorArquivosExecucao().preparar()
        self.registrador = FabricaRegistradorExecucao().criar()
        self.navegador = FabricaNavegador().criar()
        self.rastreador = RastreadorEtapas(navegador=self.navegador)
        acoes_navegador = AcoesNavegador(self.navegador, self.registrador)

        pagina_login = PaginaLogin(acoes_navegador)
        pagina_tabelas_cliente = PaginaTabelasCliente(acoes_navegador)
        reajustador_taxas = ReajustadorTaxas(
            acoes_navegador=acoes_navegador,
            pagina_tabelas_cliente=pagina_tabelas_cliente,
            valor_reajuste=self.valor_reajuste,
            rastreador=self.rastreador,
        )
        gestor_ocorrencias = GestorOcorrenciasProcessamento(acoes_navegador)
        processador_tabela = ProcessadorTabelaClientes(
            acoes_navegador=acoes_navegador,
            pagina_tabelas_cliente=pagina_tabelas_cliente,
            reajustador_taxas=reajustador_taxas,
            gestor_ocorrencias=gestor_ocorrencias,
            observador_execucao=self.observador_execucao,
            rastreador=self.rastreador,
        )
        return pagina_login, pagina_tabelas_cliente, processador_tabela

    @staticmethod
    def _validar_configuracao() -> None:
        campos_obrigatorios = []
        if not config.URL_LOGIN.strip():
            campos_obrigatorios.append("URL_LOGIN")
        if not config.EMAIL_LOGIN.strip():
            campos_obrigatorios.append("EMAIL_LOGIN")
        if not config.SENHA_LOGIN.strip():
            campos_obrigatorios.append("SENHA_LOGIN")

        if campos_obrigatorios:
            raise ValueError(
                "Preencha as configuracoes obrigatorias: "
                + ", ".join(campos_obrigatorios)
            )


RoboReajusteTaxas = AutomacaoReajusteTaxas
