"""==[DOC-FILE]===============================================================
Arquivo : src/infraestrutura/arquivos_execucao.py
Classe  : PreparadorArquivosExecucao (class)
Pacote  : src.infraestrutura
Modulo  : Infraestrutura - Preparacao de Artefatos

Papel   : Garante a existencia de logs, relatorios e arquivos auxiliares antes
          do inicio da automacao.

Conecta com:
- config - caminhos de logs, relatorios e screenshots
- csv - criacao do cabecalho do arquivo de processamento

Fluxo geral:
1) Cria diretorios obrigatorios caso nao existam.
2) Inicializa `logs/processamento.csv` com cabecalho padrao.
3) Garante a existencia de `reports/errors.log`.

Estrutura interna:
Metodos principais:
- preparar(): prepara toda a estrutura de arquivos da execucao.
[DOC-FILE-END]==============================================================="""

import csv

import config
from src.infraestrutura.retencao_artefatos import (
    limitar_csv_por_registros,
    limitar_json_lista,
    limitar_texto_por_linhas,
    manter_arquivos_mais_recentes,
)


class PreparadorArquivosExecucao:
    def preparar(self) -> None:
        config.DIRETORIO_LOGS.mkdir(parents=True, exist_ok=True)
        config.DIRETORIO_RELATORIOS.mkdir(parents=True, exist_ok=True)
        config.DIRETORIO_SCREENSHOTS.mkdir(parents=True, exist_ok=True)

        if (
            not config.ARQUIVO_LOG_PROCESSAMENTO.exists()
            or config.ARQUIVO_LOG_PROCESSAMENTO.stat().st_size == 0
        ):
            with config.ARQUIVO_LOG_PROCESSAMENTO.open(
                "w", newline="", encoding="utf-8"
            ) as arquivo_csv:
                escritor = csv.writer(arquivo_csv, delimiter=";")
                escritor.writerow(
                    [
                        "timestamp",
                        "pagina",
                        "linha",
                        "identificador",
                        "status",
                        "mensagem",
                        "screenshot",
                    ]
                )

        config.ARQUIVO_LOG_ERROS.touch(exist_ok=True)
        self._aplicar_retencao()

    def _aplicar_retencao(self) -> None:
        manter_arquivos_mais_recentes(
            config.DIRETORIO_SCREENSHOTS,
            config.MAX_SCREENSHOTS_ARMAZENADOS,
            padroes=("*.png", "*.jpg", "*.jpeg"),
        )
        limitar_csv_por_registros(
            config.ARQUIVO_LOG_PROCESSAMENTO,
            config.MAX_REGISTROS_PROCESSAMENTO,
        )
        limitar_texto_por_linhas(
            config.ARQUIVO_LOG_ERROS,
            config.MAX_REGISTROS_PROCESSAMENTO,
        )
        limitar_json_lista(
            config.DIRETORIO_LOGS / "execution_trace.json",
            config.MAX_REGISTROS_TRACE,
        )
