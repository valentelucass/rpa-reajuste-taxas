import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.ui.ui_main import JanelaPainelAutomacao, LINHAS_LOGS_POR_PAGINA


class JanelaPainelAutomacaoLogsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.janela = JanelaPainelAutomacao()

    def tearDown(self) -> None:
        self.janela.close()

    def test_logs_ficam_em_uma_unica_pagina_ate_o_limite(self) -> None:
        self.janela._adicionar_registro_log(self._criar_log(1))

        self.assertEqual(self.janela.tabela_logs.rowCount(), 1)
        self.assertEqual(
            self.janela.rotulo_contagem_logs.text(),
            "Mostrando 1-1 de 1 registros",
        )
        self.assertTrue(self.janela.botao_pagina_anterior_logs.isHidden())
        self.assertTrue(self.janela.botao_pagina_seguinte_logs.isHidden())

    def test_logs_sao_paginados_quando_ultrapassam_o_limite(self) -> None:
        total_logs = LINHAS_LOGS_POR_PAGINA + 2

        for indice in range(1, total_logs + 1):
            self.janela._adicionar_registro_log(self._criar_log(indice))

        self.assertEqual(self.janela._obter_total_paginas_logs(), 2)
        self.assertEqual(self.janela.tabela_logs.rowCount(), 2)
        self.assertEqual(
            self.janela.tabela_logs.item(0, 0).text(),
            str(LINHAS_LOGS_POR_PAGINA + 1),
        )
        self.assertEqual(self.janela.rotulo_pagina_logs.text(), "Pagina 2 de 2")
        self.assertEqual(
            self.janela.rotulo_contagem_logs.text(),
            f"Mostrando {LINHAS_LOGS_POR_PAGINA + 1}-{total_logs} de {total_logs} registros",
        )
        self.assertFalse(self.janela.botao_pagina_anterior_logs.isHidden())
        self.assertFalse(self.janela.botao_pagina_seguinte_logs.isHidden())

        self.janela._ir_para_pagina_logs_anterior()

        self.assertEqual(
            self.janela.rotulo_contagem_logs.text(),
            f"Mostrando 1-{LINHAS_LOGS_POR_PAGINA} de {total_logs} registros",
        )
        self.assertEqual(self.janela.rotulo_pagina_logs.text(), "Pagina 1 de 2")
        self.assertEqual(self.janela.tabela_logs.rowCount(), LINHAS_LOGS_POR_PAGINA)
        self.assertEqual(self.janela.tabela_logs.item(0, 0).text(), "1")

    def test_mesmo_registro_atualiza_a_linha_existente(self) -> None:
        self.janela._adicionar_registro_log(
            self._criar_log(
                42,
                status="Processando",
                mensagem="Processando registro.",
                horario="10:00:42",
            )
        )
        self.janela._adicionar_registro_log(
            self._criar_log(
                42,
                status="Sucesso",
                mensagem="Fluxo validado com sucesso.",
                horario="10:00:51",
            )
        )

        self.assertEqual(len(self.janela.registros_logs), 1)
        self.assertEqual(self.janela.tabela_logs.rowCount(), 1)
        self.assertEqual(self.janela.registros_logs[0]["status"], "Sucesso")
        self.assertEqual(
            self.janela.registros_logs[0]["mensagem"],
            "Fluxo validado com sucesso.",
        )
        self.assertEqual(self.janela.registros_logs[0]["horario"], "10:00:51")

    def test_reprocessaveis_refletem_apenas_o_status_atual(self) -> None:
        self.janela._adicionar_registro_log(
            self._criar_log(
                77,
                status="Erro",
                mensagem="Falha ao processar.",
                horario="10:01:10",
                pode_reprocessar=True,
            )
        )

        self.assertEqual(self.janela.total_logs_reprocessaveis, 1)

        self.janela._adicionar_registro_log(
            self._criar_log(
                77,
                status="Sucesso",
                mensagem="Reprocessamento concluido com sucesso.",
                horario="10:01:32",
                pode_reprocessar=False,
            )
        )

        self.assertEqual(len(self.janela.registros_logs), 1)
        self.assertEqual(self.janela.total_logs_reprocessaveis, 0)
        self.assertEqual(self.janela.registros_logs[0]["status"], "Sucesso")

    @staticmethod
    def _criar_log(
        indice: int,
        *,
        status: str = "Processando",
        mensagem: str | None = None,
        horario: str | None = None,
        pode_reprocessar: bool = False,
    ) -> dict:
        return {
            "id_linha": indice,
            "cliente": f"Cliente {indice}",
            "status": status,
            "horario": horario or f"10:00:{indice:02d}",
            "mensagem": mensagem or f"Processando cliente {indice}",
            "pode_reprocessar": pode_reprocessar,
            "numero_pagina": 1,
            "numero_linha": indice,
            "identificador": f"registro-{indice}",
        }


if __name__ == "__main__":
    unittest.main()
