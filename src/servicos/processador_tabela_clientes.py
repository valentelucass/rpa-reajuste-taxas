"""==[DOC-FILE]===============================================================
Arquivo : src/servicos/processador_tabela_clientes.py
Classe  : ProcessadorTabelaClientes (class)
Pacote  : src.servicos
Modulo  : Servicos - Loop Mestre da Tabela

Papel   : Controla o loop de paginas e de linhas da tabela, garantindo que a
          automacao percorra todos os registros e continue mesmo apos erros individuais.

Conecta com:
- src.paginas.pagina_tabelas_cliente - origem das linhas e paginacao
- src.servicos.reajustador_taxas - execucao do reajuste por linha
- src.servicos.gestor_ocorrencias - registro de sucesso/falha e recuperacao
- src.monitoramento.observador_execucao - progresso exibido no painel

Fluxo geral:
1) Le todas as linhas visiveis da pagina atual sem assumir quantidade fixa.
2) Reprocessa a linha correta mesmo apos re-renderizacoes do Vue.
3) Em caso de erro, registra evidencia e segue para a proxima linha.
4) Ao fim da pagina, avanca enquanto existir proxima pagina.

Estrutura interna:
Metodos principais:
- processar_todas_paginas(): loop principal da automacao.
- reprocessar_registro(): localiza e roda novamente um item com falha.
- _processar_pagina_atual(): executa o ciclo das linhas da pagina.
- _extrair_contexto_linha(): monta os metadados usados em log e reprocessamento.
[DOC-FILE-END]==============================================================="""

import time
import traceback
from collections import defaultdict
from typing import DefaultDict, List, Optional, Sequence

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

import config
from src.infraestrutura.acoes_navegador import AcoesNavegador
from src.infraestrutura.rastreador_etapas import RastreadorEtapas
from src.monitoramento.observador_execucao import (
    ContextoLinhaExecucao,
    ObservadorExecucaoNulo,
)
from src.paginas.pagina_tabelas_cliente import PaginaTabelasCliente
from src.servicos.gestor_ocorrencias import GestorOcorrenciasProcessamento
from src.servicos.reajustador_taxas import ReajustadorTaxas


class ProcessadorTabelaClientes:
    ASSINATURA_LINHA_VAZIA = "__LINHA_VAZIA__"

    def __init__(
        self,
        acoes_navegador: AcoesNavegador,
        pagina_tabelas_cliente: PaginaTabelasCliente,
        reajustador_taxas: ReajustadorTaxas,
        gestor_ocorrencias: GestorOcorrenciasProcessamento,
        observador_execucao: Optional[object] = None,
        rastreador: Optional[RastreadorEtapas] = None,
    ) -> None:
        self.acoes_navegador = acoes_navegador
        self.pagina_tabelas_cliente = pagina_tabelas_cliente
        self.reajustador_taxas = reajustador_taxas
        self.gestor_ocorrencias = gestor_ocorrencias
        self.observador_execucao = observador_execucao or ObservadorExecucaoNulo()
        self.rastreador = rastreador

    def processar_todas_paginas(self) -> int:
        total_processado = 0
        numero_pagina = 1

        while True:
            self.observador_execucao.validar_continuacao()
            self.acoes_navegador.registrador.info(
                "Processando pagina %s", numero_pagina
            )
            if self.rastreador:
                self.rastreador.registrar_inicio(
                    f"processar_pagina_{numero_pagina}",
                    f"Processando pagina {numero_pagina}",
                    {"pagina": numero_pagina},
                )
            total_processado += self._processar_pagina_atual(numero_pagina)
            if self.rastreador:
                self.rastreador.registrar_sucesso(
                    f"processar_pagina_{numero_pagina}",
                    {"pagina": numero_pagina, "total_processado": total_processado},
                )
            self.observador_execucao.validar_continuacao()
            if not self.pagina_tabelas_cliente.ir_para_proxima_pagina():
                break
            numero_pagina += 1

        return total_processado

    def reprocessar_registro(self, contexto_alvo: ContextoLinhaExecucao) -> bool:
        numero_pagina = 1
        while True:
            self.observador_execucao.validar_continuacao()
            linhas = self.pagina_tabelas_cliente.obter_linhas_tabela(
                aguardar_presenca=True
            )
            for indice_linha, linha in enumerate(linhas, start=1):
                contexto_linha = self._extrair_contexto_linha(
                    numero_pagina=numero_pagina,
                    numero_linha=indice_linha,
                    linha=linha,
                    assinatura_linha=self._obter_assinatura_linha(linha),
                )
                if not self._linha_corresponde_contexto(contexto_linha, contexto_alvo):
                    continue

                return self._executar_reprocessamento_linha(contexto_linha, linha)

            if not self.pagina_tabelas_cliente.ir_para_proxima_pagina():
                break
            numero_pagina += 1

        raise NoSuchElementException(
            f"Registro para reprocessamento nao localizado: {contexto_alvo.identificador}"
        )

    def _processar_pagina_atual(self, numero_pagina: int) -> int:
        linhas = self.pagina_tabelas_cliente.obter_linhas_tabela(aguardar_presenca=True)
        if not linhas:
            self.acoes_navegador.registrador.info(
                "Nenhum registro encontrado na pagina %s", numero_pagina
            )
            return 0

        total_linhas_tratadas = 0
        ocorrencias_processadas: DefaultDict[str, int] = defaultdict(int)
        linhas, assinaturas_linhas = self._obter_assinaturas_estaveis(linhas)

        for numero_linha, assinatura_linha in enumerate(assinaturas_linhas, start=1):
            self.observador_execucao.validar_continuacao()
            linha_atual = self._localizar_linha_por_assinatura(
                assinatura_linha, ocorrencias_processadas
            )
            if linha_atual is None:
                contexto_fallback = ContextoLinhaExecucao(
                    numero_pagina=numero_pagina,
                    numero_linha=numero_linha,
                    id_linha=f"sem_id_{numero_pagina}_{numero_linha}",
                    cliente=f"Linha {numero_linha}",
                    identificador=assinatura_linha or f"linha_{numero_linha}",
                    texto_linha=assinatura_linha,
                )
                mensagem = "Linha nao localizada apos re-renderizacao da tabela."
                self.gestor_ocorrencias.registrar_falha(
                    numero_pagina=numero_pagina,
                    numero_linha=numero_linha,
                    identificador=contexto_fallback.identificador,
                    mensagem=mensagem,
                )
                self.observador_execucao.registrar_falha(contexto_fallback, mensagem)
                self.acoes_navegador.registrador.error(
                    "Pagina %s linha %s: %s", numero_pagina, numero_linha, mensagem
                )
                total_linhas_tratadas += 1
                continue

            ocorrencias_processadas[assinatura_linha] += 1
            contexto_linha = self._extrair_contexto_linha(
                numero_pagina=numero_pagina,
                numero_linha=numero_linha,
                linha=linha_atual,
                assinatura_linha=assinatura_linha,
            )
            self.observador_execucao.registrar_processando(contexto_linha)

            try:
                contexto_rastreio = {
                    "pagina": numero_pagina,
                    "linha": numero_linha,
                    "cliente": contexto_linha.cliente,
                    "id_registro": contexto_linha.id_linha,
                }
                self.reajustador_taxas.processar_linha(linha_atual, contexto=contexto_rastreio)
                if not config.CONFIRMAR_REAJUSTE_FINAL:
                    mensagem = (
                        "Fluxo validado com sucesso sem confirmar o reajuste "
                        "(modo de teste)."
                    )
                else:
                    mensagem = "Reajuste aplicado com sucesso."
                self.gestor_ocorrencias.registrar_sucesso(
                    numero_pagina=numero_pagina,
                    numero_linha=numero_linha,
                    identificador=contexto_linha.identificador,
                    mensagem=mensagem,
                )
                self.observador_execucao.registrar_sucesso(contexto_linha, mensagem)
                total_linhas_tratadas += 1
            except Exception as erro:
                self.gestor_ocorrencias.registrar_falha(
                    numero_pagina=numero_pagina,
                    numero_linha=numero_linha,
                    identificador=contexto_linha.identificador,
                    mensagem=str(erro),
                )
                self.observador_execucao.registrar_falha(
                    contexto_linha, str(erro)
                )
                self.acoes_navegador.registrador.error(
                    "Erro na pagina %s linha %s (%s): %s\n%s",
                    numero_pagina,
                    numero_linha,
                    contexto_linha.identificador,
                    erro,
                    traceback.format_exc(),
                )
                self.gestor_ocorrencias.recuperar_interface_apos_erro()
                total_linhas_tratadas += 1
            finally:
                self.acoes_navegador.aguardar_carregamento_finalizar()
                self.pagina_tabelas_cliente.aguardar_resultados_pesquisa()

        return total_linhas_tratadas

    def _executar_reprocessamento_linha(
        self, contexto_linha: ContextoLinhaExecucao, linha: WebElement
    ) -> bool:
        self.observador_execucao.registrar_processando(contexto_linha)
        try:
            contexto_rastreio = {
                "pagina": contexto_linha.numero_pagina,
                "linha": contexto_linha.numero_linha,
                "cliente": contexto_linha.cliente,
                "id_registro": contexto_linha.id_linha,
                "modo": "reprocessamento",
            }
            self.reajustador_taxas.processar_linha(linha, contexto=contexto_rastreio)
            mensagem = "Reprocessamento concluido com sucesso."
            self.gestor_ocorrencias.registrar_sucesso(
                numero_pagina=contexto_linha.numero_pagina,
                numero_linha=contexto_linha.numero_linha,
                identificador=contexto_linha.identificador,
                mensagem=mensagem,
            )
            self.observador_execucao.registrar_sucesso(contexto_linha, mensagem)
            return True
        except Exception as erro:
            self.gestor_ocorrencias.registrar_falha(
                numero_pagina=contexto_linha.numero_pagina,
                numero_linha=contexto_linha.numero_linha,
                identificador=contexto_linha.identificador,
                mensagem=str(erro),
            )
            self.observador_execucao.registrar_falha(contexto_linha, str(erro))
            self.acoes_navegador.registrador.error(
                "Erro no reprocessamento %s: %s\n%s",
                contexto_linha.identificador,
                erro,
                traceback.format_exc(),
            )
            self.gestor_ocorrencias.recuperar_interface_apos_erro()
            raise
        finally:
            self.acoes_navegador.aguardar_carregamento_finalizar()
            self.pagina_tabelas_cliente.aguardar_resultados_pesquisa()

    def _montar_assinaturas_linhas(self, linhas: Sequence[WebElement]) -> List[str]:
        return [self._obter_assinatura_linha(linha) for linha in linhas]

    def _obter_assinaturas_estaveis(
        self, linhas: List[WebElement]
    ) -> tuple[List[WebElement], List[str]]:
        for tentativa in range(3):
            assinaturas = self._montar_assinaturas_linhas(linhas)
            if not all(a == self.ASSINATURA_LINHA_VAZIA for a in assinaturas):
                return linhas, assinaturas
            self.acoes_navegador.registrador.info(
                "Assinaturas instáveis (tentativa %s/3), aguardando re-renderizacao.",
                tentativa + 1,
            )
            time.sleep(1)
            linhas = self.pagina_tabelas_cliente.obter_linhas_tabela(
                aguardar_presenca=True
            )
            if not linhas:
                return [], []
        return linhas, self._montar_assinaturas_linhas(linhas)

    def _obter_assinatura_linha(self, linha: WebElement) -> str:
        texto_linha = self.acoes_navegador.normalizar_espacos(
            self.acoes_navegador.texto_seguro(linha)
        )
        return texto_linha or self.ASSINATURA_LINHA_VAZIA

    def _extrair_contexto_linha(
        self,
        numero_pagina: int,
        numero_linha: int,
        linha: WebElement,
        assinatura_linha: str,
    ) -> ContextoLinhaExecucao:
        texto_linha = self.acoes_navegador.texto_seguro(linha).strip()
        partes_texto = [parte.strip() for parte in texto_linha.splitlines() if parte.strip()]
        cliente = partes_texto[0] if partes_texto else f"Registro {numero_linha}"
        id_linha = (
            (linha.get_attribute("data-id") or "").strip()
            or f"pagina_{numero_pagina}_linha_{numero_linha}"
        )
        identificador = (
            assinatura_linha
            if assinatura_linha != self.ASSINATURA_LINHA_VAZIA
            else id_linha
        )
        return ContextoLinhaExecucao(
            numero_pagina=numero_pagina,
            numero_linha=numero_linha,
            id_linha=id_linha,
            cliente=cliente,
            identificador=identificador,
            texto_linha=texto_linha or assinatura_linha,
        )

    def _localizar_linha_por_assinatura(
        self,
        assinatura_alvo: str,
        ocorrencias_processadas: DefaultDict[str, int],
    ) -> Optional[WebElement]:
        linhas = self.pagina_tabelas_cliente.obter_linhas_tabela(aguardar_presenca=False)
        ocorrencia_desejada = ocorrencias_processadas[assinatura_alvo] + 1
        ocorrencia_atual = 0

        for linha in linhas:
            assinatura_linha = self._obter_assinatura_linha(linha)
            if assinatura_linha == assinatura_alvo:
                ocorrencia_atual += 1
                if ocorrencia_atual == ocorrencia_desejada:
                    return linha

        return None

    @staticmethod
    def _linha_corresponde_contexto(
        contexto_linha: ContextoLinhaExecucao,
        contexto_alvo: ContextoLinhaExecucao,
    ) -> bool:
        if contexto_linha.id_linha and contexto_linha.id_linha == contexto_alvo.id_linha:
            return True
        if (
            contexto_linha.identificador
            and contexto_linha.identificador == contexto_alvo.identificador
        ):
            return True
        return (
            bool(contexto_linha.cliente)
            and bool(contexto_alvo.cliente)
            and contexto_linha.cliente == contexto_alvo.cliente
        )
