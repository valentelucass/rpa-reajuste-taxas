import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import config
from src.servicos.processador_tabela_clientes import ProcessadorTabelaClientes


class FakeLinha:
    def __init__(self, data_id: str, texto: str) -> None:
        self._data_id = data_id
        self.text = texto

    def get_attribute(self, nome: str) -> str:
        if nome == "data-id":
            return self._data_id
        return ""


class FakePagina:
    def __init__(self, paginas: list[list[FakeLinha]]) -> None:
        self.paginas = paginas
        self.indice_pagina = 0

    def obter_linhas_tabela(self, aguardar_presenca: bool) -> list[FakeLinha]:
        return list(self.paginas[self.indice_pagina])

    def ir_para_proxima_pagina(self) -> bool:
        if self.indice_pagina + 1 >= len(self.paginas):
            return False
        self.indice_pagina += 1
        return True

    def aguardar_resultados_pesquisa(self) -> None:
        return None


class ProcessadorTabelaClientesTest(unittest.TestCase):
    def _criar_processador(
        self,
        paginas: list[list[FakeLinha]],
        reajustador: MagicMock | None = None,
    ) -> tuple[ProcessadorTabelaClientes, MagicMock, MagicMock, FakePagina]:
        acoes = SimpleNamespace(
            registrador=MagicMock(),
            normalizar_espacos=lambda texto: " ".join((texto or "").split()),
            texto_seguro=lambda linha: linha.text,
            aguardar_carregamento_finalizar=MagicMock(),
        )
        pagina = FakePagina(paginas)
        reajustador = reajustador or MagicMock()
        gestor = MagicMock()
        observador = MagicMock()

        processador = ProcessadorTabelaClientes(
            acoes_navegador=acoes,
            pagina_tabelas_cliente=pagina,
            reajustador_taxas=reajustador,
            gestor_ocorrencias=gestor,
            observador_execucao=observador,
            rastreador=None,
        )
        return processador, gestor, observador, pagina

    def test_processa_todas_as_paginas_com_quantidade_dinamica(self) -> None:
        paginas = [
            [FakeLinha("1", "Cliente A"), FakeLinha("2", "Cliente B")],
            [FakeLinha("3", "Cliente C")],
            [FakeLinha("4", "Cliente D"), FakeLinha("5", "Cliente E"), FakeLinha("6", "Cliente F")],
        ]
        reajustador = MagicMock()
        processador, gestor, observador, pagina = self._criar_processador(
            paginas, reajustador=reajustador
        )

        with patch.object(config, "CONFIRMAR_REAJUSTE_FINAL", True):
            total = processador.processar_todas_paginas()

        self.assertEqual(total, 6)
        self.assertEqual(reajustador.processar_linha.call_count, 6)
        self.assertEqual(gestor.registrar_sucesso.call_count, 6)
        self.assertEqual(gestor.registrar_falha.call_count, 0)
        self.assertEqual(pagina.indice_pagina, 2)
        self.assertEqual(observador.registrar_processando.call_count, 6)

    def test_continua_apos_falha_isolada(self) -> None:
        paginas = [[
            FakeLinha("1", "Cliente A"),
            FakeLinha("2", "Cliente B"),
            FakeLinha("3", "Cliente C"),
        ]]
        reajustador = MagicMock()
        reajustador.processar_linha.side_effect = [None, RuntimeError("falha"), None]
        processador, gestor, _, _ = self._criar_processador(
            paginas, reajustador=reajustador
        )

        with patch.object(config, "CONFIRMAR_REAJUSTE_FINAL", True):
            total = processador.processar_todas_paginas()

        self.assertEqual(total, 3)
        self.assertEqual(gestor.registrar_sucesso.call_count, 2)
        self.assertEqual(gestor.registrar_falha.call_count, 1)
        self.assertEqual(gestor.recuperar_interface_apos_erro.call_count, 1)

    def test_registra_mensagem_de_modo_teste_quando_confirmacao_esta_bloqueada(self) -> None:
        paginas = [[FakeLinha("1", "Cliente A")]]
        processador, gestor, _, _ = self._criar_processador(paginas)

        with patch.object(config, "CONFIRMAR_REAJUSTE_FINAL", False):
            processador.processar_todas_paginas()

        mensagem = gestor.registrar_sucesso.call_args.kwargs["mensagem"]
        self.assertIn("modo de teste", mensagem.lower())


if __name__ == "__main__":
    unittest.main()
