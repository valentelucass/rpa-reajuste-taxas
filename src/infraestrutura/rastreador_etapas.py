"""==[DOC-FILE]===============================================================
Arquivo : src/infraestrutura/rastreador_etapas.py
Classe  : RastreadorEtapas (class)
Pacote  : src.infraestrutura
Modulo  : Infraestrutura - Rastreamento de Execucao (Step Tracking)

Papel   : Registra cada etapa da automacao em formato JSON estruturado,
          permitindo identificar exatamente onde o robo parou e facilitar
          analise automatizada por IA.

Conecta com:
- config - caminhos de logs e screenshots
- src.aplicacao - orquestracao principal do robo
- src.servicos - processamento e reajuste por linha
- src.infraestrutura.acoes_navegador - captura de screenshot em erro

Fluxo geral:
1) Cada etapa gera registros START, SUCCESS ou ERROR em JSON.
2) Um arquivo current_step.json mantem sempre a ultima etapa executada.
3) Em caso de erro, captura screenshot automaticamente.
4) Context manager permite uso limpo com blocos `with`.

Estrutura interna:
Metodos principais:
- etapa(): context manager que registra START/SUCCESS/ERROR automaticamente.
- registrar_inicio(): registra inicio de uma etapa.
- registrar_sucesso(): registra conclusao bem-sucedida.
- registrar_erro(): registra falha com mensagem e screenshot.
[DOC-FILE-END]==============================================================="""

import json
import traceback
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from selenium.common.exceptions import WebDriverException

import config
from src.infraestrutura.retencao_artefatos import (
    limitar_json_lista,
    manter_arquivos_mais_recentes,
)


def _timestamp_atual() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _timestamp_arquivo() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class RastreadorEtapas:
    def __init__(self, navegador=None) -> None:
        self.navegador = navegador
        self._arquivo_trace = config.DIRETORIO_LOGS / "execution_trace.json"
        self._arquivo_etapa_atual = config.DIRETORIO_LOGS / "current_step.json"
        self._registros: list = []
        self._carregar_registros_existentes()

    def _carregar_registros_existentes(self) -> None:
        if self._arquivo_trace.exists() and self._arquivo_trace.stat().st_size > 0:
            try:
                self._registros = json.loads(
                    self._arquivo_trace.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                self._registros = []

    def reiniciar_sessao(self) -> None:
        marcador = {
            "timestamp": _timestamp_atual(),
            "step": "__session_start__",
            "description": "Nova sessao de execucao iniciada",
            "status": "info",
            "context": {},
        }
        self._registros.append(marcador)
        self._salvar()

    @contextmanager
    def etapa(
        self,
        nome_etapa: str,
        descricao: str,
        contexto: Optional[Dict[str, Any]] = None,
    ) -> Generator[None, None, None]:
        self.registrar_inicio(nome_etapa, descricao, contexto)
        try:
            yield
            self.registrar_sucesso(nome_etapa, contexto)
        except Exception as erro:
            self.registrar_erro(nome_etapa, str(erro), contexto)
            raise

    def registrar_inicio(
        self,
        nome_etapa: str,
        descricao: str,
        contexto: Optional[Dict[str, Any]] = None,
    ) -> None:
        registro = {
            "timestamp": _timestamp_atual(),
            "step": nome_etapa,
            "description": descricao,
            "status": "start",
            "context": contexto or {},
        }
        self._registros.append(registro)
        self._atualizar_etapa_atual(nome_etapa)
        self._salvar()

    def registrar_sucesso(
        self,
        nome_etapa: str,
        contexto: Optional[Dict[str, Any]] = None,
    ) -> None:
        registro = {
            "timestamp": _timestamp_atual(),
            "step": nome_etapa,
            "description": f"Etapa '{nome_etapa}' concluida com sucesso.",
            "status": "success",
            "context": contexto or {},
        }
        self._registros.append(registro)
        self._salvar()

    def registrar_erro(
        self,
        nome_etapa: str,
        mensagem_erro: str,
        contexto: Optional[Dict[str, Any]] = None,
    ) -> None:
        screenshot_path = self._capturar_screenshot(nome_etapa)
        registro = {
            "timestamp": _timestamp_atual(),
            "step": nome_etapa,
            "description": f"Erro na etapa '{nome_etapa}'.",
            "status": "error",
            "error_message": mensagem_erro,
            "error_traceback": traceback.format_exc(),
            "screenshot": str(screenshot_path) if screenshot_path else None,
            "context": contexto or {},
        }
        self._registros.append(registro)
        self._atualizar_etapa_atual(nome_etapa, erro=mensagem_erro)
        self._salvar()

    def _capturar_screenshot(self, nome_etapa: str) -> Optional[Path]:
        if self.navegador is None:
            return None
        caminho = (
            config.DIRETORIO_SCREENSHOTS
            / f"erro_{nome_etapa}_{_timestamp_arquivo()}.png"
        )
        try:
            config.DIRETORIO_SCREENSHOTS.mkdir(parents=True, exist_ok=True)
            self.navegador.save_screenshot(str(caminho))
            manter_arquivos_mais_recentes(
                config.DIRETORIO_SCREENSHOTS,
                config.MAX_SCREENSHOTS_ARMAZENADOS,
                padroes=("*.png", "*.jpg", "*.jpeg"),
            )
            return caminho
        except (WebDriverException, OSError):
            return None

    def _atualizar_etapa_atual(
        self, nome_etapa: str, erro: Optional[str] = None
    ) -> None:
        dados: Dict[str, Any] = {
            "current_step": nome_etapa,
            "timestamp": _timestamp_atual(),
        }
        if erro:
            dados["last_error"] = erro
        try:
            self._arquivo_etapa_atual.write_text(
                json.dumps(dados, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def _salvar(self) -> None:
        try:
            config.DIRETORIO_LOGS.mkdir(parents=True, exist_ok=True)
            self._arquivo_trace.write_text(
                json.dumps(self._registros, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            limitar_json_lista(
                self._arquivo_trace,
                config.MAX_REGISTROS_TRACE,
            )
        except OSError:
            pass
