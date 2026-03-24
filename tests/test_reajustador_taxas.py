import unittest
from unittest.mock import MagicMock, patch

import config
from src.servicos.reajustador_taxas import ReajustadorTaxas


class FakeIcone:
    def __init__(self, classe: str) -> None:
        self._classe = classe

    def get_attribute(self, nome: str) -> str:
        if nome == "class":
            return self._classe
        return ""


class FakeBotaoConsiderar:
    def __init__(self, icone: FakeIcone) -> None:
        self.icone = icone

    def find_elements(self, _by: str, _selector: str) -> list[FakeIcone]:
        return [self.icone]


class ReajustadorTaxasTest(unittest.TestCase):
    def test_marcar_considerar_todos_clica_no_icone_ate_confirmar_selecao(self) -> None:
        acoes = MagicMock()
        icone = FakeIcone("fa fa-square")
        botao = FakeBotaoConsiderar(icone)
        acoes.navegador = MagicMock()

        reajustador = ReajustadorTaxas(
            acoes_navegador=acoes,
            pagina_tabelas_cliente=MagicMock(),
            valor_reajuste=15.0,
            rastreador=None,
        )

        acoes.buscar_primeiro_por_nome_seletor.return_value = botao

        def clicar(_alvo):
            icone._classe = "fa fa-check-square"
            return None

        acoes.clicar_com_seguranca.side_effect = clicar
        reajustador._marcar_considerar_todos_trechos(MagicMock())

        acoes.clicar_com_seguranca.assert_called_once_with(icone)

    def test_confirmacao_bloqueada_cancela_swal_e_fecha_modal(self) -> None:
        acoes = MagicMock()
        acoes.buscar_primeiro_por_nome_seletor.return_value = None
        botao_cancelar = object()
        acoes.aguardar_seletor.return_value = botao_cancelar
        reajustador = ReajustadorTaxas(
            acoes_navegador=acoes,
            pagina_tabelas_cliente=MagicMock(),
            valor_reajuste=15.0,
            rastreador=None,
        )
        modal = object()

        with patch.object(config, "CONFIRMAR_REAJUSTE_FINAL", False):
            reajustador._confirmar_popup_reajuste(modal)

        acoes.aguardar_seletor.assert_called_once_with(
            "botao_cancelar_swal", condicao="clicavel", timeout=10
        )
        acoes.clicar_com_seguranca.assert_called_once_with(botao_cancelar)
        acoes.clicar_por_texto.assert_called_once_with(
            config.ROTULOS_REAJUSTE["fechar"], contexto=modal, timeout=5
        )

    def test_confirmacao_real_clica_em_sim(self) -> None:
        acoes = MagicMock()
        acoes.buscar_primeiro_por_nome_seletor.return_value = None
        botao_confirmar = object()
        acoes.aguardar_seletor.return_value = botao_confirmar
        reajustador = ReajustadorTaxas(
            acoes_navegador=acoes,
            pagina_tabelas_cliente=MagicMock(),
            valor_reajuste=15.0,
            rastreador=None,
        )

        with patch.object(config, "CONFIRMAR_REAJUSTE_FINAL", True):
            reajustador._confirmar_popup_reajuste(object())

        acoes.aguardar_seletor.assert_called_once_with(
            "botao_confirmar_swal", condicao="clicavel", timeout=10
        )
        acoes.clicar_com_seguranca.assert_called_once_with(botao_confirmar)
        acoes.clicar_por_texto.assert_not_called()

    def test_preenche_valor_com_valor_configurado(self) -> None:
        acoes = MagicMock()
        campo_valor = object()
        acoes.buscar_primeiro_por_nome_seletor.return_value = campo_valor
        reajustador = ReajustadorTaxas(
            acoes_navegador=acoes,
            pagina_tabelas_cliente=MagicMock(),
            valor_reajuste=27.5,
            rastreador=None,
        )

        reajustador._preencher_valor_reajuste(object())

        acoes.limpar_e_digitar.assert_called_once_with(campo_valor, "27.5")


if __name__ == "__main__":
    unittest.main()
