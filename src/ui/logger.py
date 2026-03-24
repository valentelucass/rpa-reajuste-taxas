"""==[DOC-FILE]===============================================================
Arquivo : src/ui/logger.py
Classe  : RegistroLogPainel, ResumoExecucaoPainel, CentralLogsPainel
Pacote  : src.ui
Modulo  : UI - Estado e Historico do Painel

Papel   : Mantem o estado exibido no dashboard desktop, consolidando
          estatisticas, progresso e eventos apresentados ao usuario.

Conecta com:
- src.monitoramento.observador_execucao - contexto de linha processada
- src.ui.rpa_worker - produtor dos eventos do painel
- src.ui.ui_main - consumidor do estado consolidado

Fluxo geral:
1) Recebe eventos de processando, sucesso, falha e mensagens de sistema.
2) Atualiza contadores de total, processados, sucessos e falhas.
3) Converte os registros para dicionarios consumidos pela interface Qt.

Estrutura interna:
Classes principais:
- RegistroLogPainel: representa uma linha do log exibido na tabela.
- ResumoExecucaoPainel: agrega indicadores numericos do painel.
- CentralLogsPainel: coordena o estado e gera snapshots de progresso.
[DOC-FILE-END]==============================================================="""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, Optional

from src.monitoramento.observador_execucao import ContextoLinhaExecucao


@dataclass(slots=True)
class RegistroLogPainel:
    id_linha: str
    cliente: str
    status: str
    mensagem: str
    horario: str
    identificador: str
    numero_pagina: int
    numero_linha: int
    pode_reprocessar: bool

    def para_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class ResumoExecucaoPainel:
    total_registros: int = 0
    processados: int = 0
    sucessos: int = 0
    falhas: int = 0

    def para_dict(self) -> Dict[str, int]:
        return asdict(self)


class CentralLogsPainel:
    def __init__(self) -> None:
        self.reiniciar()

    def reiniciar(self) -> None:
        self.estatisticas = ResumoExecucaoPainel()
        self.contexto_em_processamento: Optional[ContextoLinhaExecucao] = None

    def definir_total_registros(self, total_registros: int) -> None:
        self.estatisticas.total_registros = max(0, total_registros)

    def registrar_processando(
        self,
        contexto: ContextoLinhaExecucao,
        mensagem: str = "Processando registro.",
    ) -> RegistroLogPainel:
        self.contexto_em_processamento = contexto
        return self._criar_registro(contexto, "Processando", mensagem, False)

    def registrar_sucesso(
        self,
        contexto: ContextoLinhaExecucao,
        mensagem: str,
    ) -> RegistroLogPainel:
        self.contexto_em_processamento = None
        self.estatisticas.processados += 1
        self.estatisticas.sucessos += 1
        return self._criar_registro(contexto, "Sucesso", mensagem, False)

    def registrar_falha(
        self,
        contexto: ContextoLinhaExecucao,
        mensagem: str,
    ) -> RegistroLogPainel:
        self.contexto_em_processamento = None
        self.estatisticas.processados += 1
        self.estatisticas.falhas += 1
        return self._criar_registro(contexto, "Erro", mensagem, True)

    def registrar_mensagem_sistema(
        self,
        status: str,
        mensagem: str,
    ) -> RegistroLogPainel:
        return RegistroLogPainel(
            id_linha="-",
            cliente="Sistema",
            status=status,
            mensagem=mensagem,
            horario=datetime.now().strftime("%H:%M:%S"),
            identificador="sistema",
            numero_pagina=0,
            numero_linha=0,
            pode_reprocessar=False,
        )

    def obter_progresso(self) -> Dict[str, int]:
        total = self.estatisticas.total_registros
        atual = self.estatisticas.processados
        if self.contexto_em_processamento is not None and total > atual:
            atual += 1

        percentual = 0
        if total > 0:
            percentual = min(100, int((atual / total) * 100))

        return {
            "atual": atual,
            "total": total,
            "percentual": percentual,
        }

    def _criar_registro(
        self,
        contexto: ContextoLinhaExecucao,
        status: str,
        mensagem: str,
        pode_reprocessar: bool,
    ) -> RegistroLogPainel:
        return RegistroLogPainel(
            id_linha=contexto.id_linha,
            cliente=contexto.cliente,
            status=status,
            mensagem=mensagem,
            horario=datetime.now().strftime("%H:%M:%S"),
            identificador=contexto.identificador,
            numero_pagina=contexto.numero_pagina,
            numero_linha=contexto.numero_linha,
            pode_reprocessar=pode_reprocessar,
        )
