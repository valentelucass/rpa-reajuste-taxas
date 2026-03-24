"""==[DOC-FILE]===============================================================
Arquivo : src/infraestrutura/registrador_execucao.py
Classe  : FabricaRegistradorExecucao (class)
Pacote  : src.infraestrutura
Modulo  : Infraestrutura - Logging Tecnico

Papel   : Cria o logger tecnico persistido em arquivo, usado para registrar
          diagnosticos, stack traces e ocorrencias de execucao da automacao.

Conecta com:
- config - caminho do arquivo `reports/errors.log`
- logging - biblioteca padrao de registro tecnico

Fluxo geral:
1) Cria ou recupera o logger do robo.
2) Limpa handlers antigos para evitar duplicidade.
3) Liga o FileHandler apontando para o arquivo de erros.

Estrutura interna:
Metodos principais:
- criar(): devolve o logger pronto para uso em toda a execucao.
[DOC-FILE-END]==============================================================="""

import logging
from logging.handlers import RotatingFileHandler

import config


class FabricaRegistradorExecucao:
    def criar(self) -> logging.Logger:
        registrador = logging.getLogger("robo_reajuste_taxas")
        registrador.setLevel(logging.INFO)
        registrador.handlers.clear()
        registrador.propagate = False

        formatador = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        manipulador_arquivo = RotatingFileHandler(
            config.ARQUIVO_LOG_ERROS,
            maxBytes=config.MAX_BYTES_LOG_ERROS,
            backupCount=config.MAX_BACKUPS_LOG_ERROS,
            encoding="utf-8",
        )
        manipulador_arquivo.setFormatter(formatador)
        manipulador_arquivo.setLevel(logging.INFO)
        registrador.addHandler(manipulador_arquivo)
        return registrador
