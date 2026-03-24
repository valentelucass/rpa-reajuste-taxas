"""==[DOC-FILE]===============================================================
Arquivo : src/monitoramento/observador_execucao.py
Classe  : ExecucaoInterrompida, ContextoLinhaExecucao, ContratoObservadorExecucao,
          ObservadorExecucaoVazio
Pacote  : src.monitoramento
Modulo  : Monitoramento - Contratos de Execucao

Papel   : Define os objetos trafegados durante o processamento e o contrato
          observado pela automacao para reportar progresso, sucesso, falha e parada.

Conecta com:
- src.aplicacao.robo_reajuste_taxas - emissor dos eventos de execucao
- src.servicos.processador_tabela_clientes - produtor dos contextos de linha
- src.ui.rpa_worker - observador concreto do painel

Fluxo geral:
1) Cada linha processada gera um ContextoLinhaExecucao.
2) O observador recebe eventos de processando, sucesso, falha e mensagens de sistema.
3) Em caso de pedido de parada, validar_continuacao() dispara ExecucaoInterrompida.

Estrutura interna:
Objetos principais:
- ExecucaoInterrompida: excecao de parada controlada.
- ContextoLinhaExecucao: dados minimos de rastreabilidade por registro.
- ContratoObservadorExecucao: protocolo da comunicacao entre robo e painel.
- ObservadorExecucaoVazio: implementacao neutra usada quando nao ha monitoramento.
[DOC-FILE-END]==============================================================="""

from dataclasses import dataclass
from typing import Protocol


class ExecucaoInterrompida(Exception):
    """Sinaliza que a automacao deve interromper o fluxo de forma controlada."""


@dataclass(slots=True)
class ContextoLinhaExecucao:
    numero_pagina: int
    numero_linha: int
    id_linha: str
    cliente: str
    identificador: str
    texto_linha: str


class ContratoObservadorExecucao(Protocol):
    def definir_total_registros(self, total_registros: int) -> None: ...

    def registrar_processando(self, contexto: ContextoLinhaExecucao) -> None: ...

    def registrar_sucesso(
        self, contexto: ContextoLinhaExecucao, mensagem: str
    ) -> None: ...

    def registrar_falha(
        self, contexto: ContextoLinhaExecucao, mensagem: str
    ) -> None: ...

    def registrar_mensagem_sistema(self, status: str, mensagem: str) -> None: ...

    def deve_interromper(self) -> bool: ...

    def validar_continuacao(self) -> None: ...


class ObservadorExecucaoVazio:
    def definir_total_registros(self, total_registros: int) -> None:
        return None

    def registrar_processando(self, contexto: ContextoLinhaExecucao) -> None:
        return None

    def registrar_sucesso(
        self, contexto: ContextoLinhaExecucao, mensagem: str
    ) -> None:
        return None

    def registrar_falha(
        self, contexto: ContextoLinhaExecucao, mensagem: str
    ) -> None:
        return None

    def registrar_mensagem_sistema(self, status: str, mensagem: str) -> None:
        return None

    def deve_interromper(self) -> bool:
        return False

    def validar_continuacao(self) -> None:
        if self.deve_interromper():
            raise ExecucaoInterrompida("Execucao interrompida pelo usuario.")


ObservadorExecucaoNulo = ObservadorExecucaoVazio
