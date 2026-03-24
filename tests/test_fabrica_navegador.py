import unittest
from unittest.mock import MagicMock, patch

from selenium.common.exceptions import WebDriverException

import config
from src.infraestrutura.fabrica_navegador import FabricaNavegador


class FabricaNavegadorTest(unittest.TestCase):
    @patch("src.infraestrutura.fabrica_navegador.ServicoEdge")
    @patch("src.infraestrutura.fabrica_navegador.ServicoChrome")
    @patch("src.infraestrutura.fabrica_navegador.webdriver.Edge")
    @patch("src.infraestrutura.fabrica_navegador.webdriver.Chrome")
    def test_criar_prioriza_chrome_quando_disponivel(
        self,
        chrome_mock,
        edge_mock,
        _servico_chrome_mock,
        _servico_edge_mock,
    ) -> None:
        navegador_chrome = MagicMock()
        chrome_mock.return_value = navegador_chrome

        navegador = FabricaNavegador().criar()

        self.assertIs(navegador, navegador_chrome)
        chrome_mock.assert_called_once()
        edge_mock.assert_not_called()
        navegador_chrome.set_page_load_timeout.assert_called_once_with(
            config.TEMPO_MAXIMO_CARREGAMENTO
        )

    @patch("src.infraestrutura.fabrica_navegador.ServicoEdge")
    @patch("src.infraestrutura.fabrica_navegador.ServicoChrome")
    @patch("src.infraestrutura.fabrica_navegador.webdriver.Edge")
    @patch("src.infraestrutura.fabrica_navegador.webdriver.Chrome")
    def test_criar_cai_para_edge_quando_chrome_falha(
        self,
        chrome_mock,
        edge_mock,
        _servico_chrome_mock,
        _servico_edge_mock,
    ) -> None:
        chrome_mock.side_effect = WebDriverException("chrome indisponivel")
        navegador_edge = MagicMock()
        edge_mock.return_value = navegador_edge

        navegador = FabricaNavegador().criar()

        self.assertIs(navegador, navegador_edge)
        chrome_mock.assert_called_once()
        edge_mock.assert_called_once()
        navegador_edge.set_page_load_timeout.assert_called_once_with(
            config.TEMPO_MAXIMO_CARREGAMENTO
        )

    @patch("src.infraestrutura.fabrica_navegador.ServicoEdge")
    @patch("src.infraestrutura.fabrica_navegador.ServicoChrome")
    @patch("src.infraestrutura.fabrica_navegador.webdriver.Edge")
    @patch("src.infraestrutura.fabrica_navegador.webdriver.Chrome")
    def test_criar_falha_quando_chrome_e_edge_indisponiveis(
        self,
        chrome_mock,
        edge_mock,
        _servico_chrome_mock,
        _servico_edge_mock,
    ) -> None:
        chrome_mock.side_effect = WebDriverException("chrome indisponivel")
        edge_mock.side_effect = WebDriverException("edge indisponivel")

        with self.assertRaisesRegex(RuntimeError, "Chrome ou Edge"):
            FabricaNavegador().criar()


if __name__ == "__main__":
    unittest.main()
