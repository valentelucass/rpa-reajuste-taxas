"""==[DOC-FILE]===============================================================
Arquivo : src/ui/rpa_worker.py
Classe  : TrabalhadorExecucaoRpa (class)
Pacote  : src.ui
Modulo  : UI - Thread de Execucao

Papel   : Executa o robo de reajuste em uma thread separada do Qt, emitindo
          sinais de progresso, status e logs sem travar a interface.

Conecta com:
- src.aplicacao.robo_reajuste_taxas - automacao principal do Selenium
- src.monitoramento.observador_execucao - contrato observado pelo robo
- src.ui.logger - consolidacao do estado exibido

Fluxo geral:
1) Inicia uma execucao completa ou um reprocessamento de item.
2) Cria a automacao e se registra como observador do processamento.
3) Emite sinais para atualizar painel, progresso, status e logs.
4) Garante encerramento do navegador mesmo em falhas.

Estrutura interna:
Metodos principais:
- run(): executa o fluxo principal da thread.
- solicitar_parada(): marca o pedido de interrupcao controlada.
- registrar_processando/registrar_sucesso/registrar_falha(): repassam eventos ao painel.
- validar_continuacao(): interrompe o fluxo quando a parada foi solicitada.
[DOC-FILE-END]==============================================================="""

from typing import Optional

from PySide6.QtCore import QThread, Signal

from src.aplicacao.robo_reajuste_taxas import AutomacaoReajusteTaxas
from src.monitoramento.observador_execucao import (
    ContextoLinhaExecucao,
    ExecucaoInterrompida,
)
from src.ui.logger import CentralLogsPainel


class TrabalhadorExecucaoRpa(QThread):
    painel_limpo = Signal()
    status_alterado = Signal(str)
    estatisticas_atualizadas = Signal(dict)
    progresso_atualizado = Signal(dict)
    registro_log_adicionado = Signal(dict)
    erro_fatal = Signal(str)
    execucao_encerrada = Signal(dict)

    def __init__(
        self,
        valor_reajuste: float,
        modo_execucao: str = "completa",
        contexto_reprocessamento: Optional[dict] = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.valor_reajuste = valor_reajuste
        self.modo_execucao = modo_execucao
        self.contexto_reprocessamento = contexto_reprocessamento or {}
        self.central_logs = CentralLogsPainel()
        self.parada_solicitada = False
        self.robo: Optional[AutomacaoReajusteTaxas] = None

    def solicitar_parada(self) -> None:
        self.parada_solicitada = True
        registro = self.central_logs.registrar_mensagem_sistema(
            "Parado",
            "Solicitacao de parada recebida. Aguardando etapa atual finalizar.",
        )
        self.registro_log_adicionado.emit(registro.para_dict())

    def run(self) -> None:
        if self.modo_execucao == "completa":
            self.central_logs.reiniciar()
            self.painel_limpo.emit()

        self.status_alterado.emit("Executando")
        self._emitir_estado_painel()

        try:
            self.robo = AutomacaoReajusteTaxas(
                valor_reajuste=self.valor_reajuste,
                observador_execucao=self,
            )
            if self.modo_execucao == "reprocessamento":
                self.robo.reprocessar_registro(self._montar_contexto_reprocessamento())
            else:
                self.robo.executar()

            if not self.parada_solicitada:
                self.status_alterado.emit("Parado")
            self.execucao_encerrada.emit(
                {
                    "status": "Parado",
                    "estatisticas": self.central_logs.estatisticas.para_dict(),
                }
            )
        except ExecucaoInterrompida as erro:
            registro = self.central_logs.registrar_mensagem_sistema("Parado", str(erro))
            self.registro_log_adicionado.emit(registro.para_dict())
            self.status_alterado.emit("Parado")
            self.execucao_encerrada.emit(
                {
                    "status": "Parado",
                    "estatisticas": self.central_logs.estatisticas.para_dict(),
                }
            )
        except Exception as erro:
            registro = self.central_logs.registrar_mensagem_sistema("Erro", str(erro))
            self.registro_log_adicionado.emit(registro.para_dict())
            self.status_alterado.emit("Erro")
            self.erro_fatal.emit(str(erro))
            self.execucao_encerrada.emit(
                {
                    "status": "Erro",
                    "estatisticas": self.central_logs.estatisticas.para_dict(),
                }
            )
        finally:
            if self.robo:
                self.robo.encerrar()
                self.robo = None

    def definir_total_registros(self, total_registros: int) -> None:
        self.central_logs.definir_total_registros(total_registros)
        self._emitir_estado_painel()

    def registrar_processando(self, contexto: ContextoLinhaExecucao) -> None:
        registro = self.central_logs.registrar_processando(contexto)
        self.registro_log_adicionado.emit(registro.para_dict())
        self._emitir_estado_painel()

    def registrar_sucesso(
        self,
        contexto: ContextoLinhaExecucao,
        mensagem: str,
    ) -> None:
        registro = self.central_logs.registrar_sucesso(contexto, mensagem)
        self.registro_log_adicionado.emit(registro.para_dict())
        self._emitir_estado_painel()

    def registrar_falha(self, contexto: ContextoLinhaExecucao, mensagem: str) -> None:
        registro = self.central_logs.registrar_falha(contexto, mensagem)
        self.registro_log_adicionado.emit(registro.para_dict())
        self._emitir_estado_painel()

    def registrar_mensagem_sistema(self, status: str, mensagem: str) -> None:
        registro = self.central_logs.registrar_mensagem_sistema(status, mensagem)
        self.registro_log_adicionado.emit(registro.para_dict())
        if status in {"Parado", "Executando", "Erro"}:
            self.status_alterado.emit(status)

    def deve_interromper(self) -> bool:
        return self.parada_solicitada

    def validar_continuacao(self) -> None:
        if self.deve_interromper():
            raise ExecucaoInterrompida("Execucao interrompida pelo usuario.")

    def _montar_contexto_reprocessamento(self) -> ContextoLinhaExecucao:
        return ContextoLinhaExecucao(
            numero_pagina=int(self.contexto_reprocessamento.get("numero_pagina", 0)),
            numero_linha=int(self.contexto_reprocessamento.get("numero_linha", 0)),
            id_linha=str(self.contexto_reprocessamento.get("id_linha", "")),
            cliente=str(self.contexto_reprocessamento.get("cliente", "")),
            identificador=str(self.contexto_reprocessamento.get("identificador", "")),
            texto_linha=str(self.contexto_reprocessamento.get("cliente", "")),
        )

    def _emitir_estado_painel(self) -> None:
        self.estatisticas_atualizadas.emit(self.central_logs.estatisticas.para_dict())
        self.progresso_atualizado.emit(self.central_logs.obter_progresso())
