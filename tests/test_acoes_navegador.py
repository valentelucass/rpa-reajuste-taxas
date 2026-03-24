import logging
import unittest
from unittest.mock import patch

import config
from src.infraestrutura.acoes_navegador import AcoesNavegador


class FakeElement:
    def __init__(
        self,
        *,
        element_id: str,
        displayed: bool = True,
        enabled: bool = True,
        attrs: dict[str, str] | None = None,
        ancestors: list["FakeElement"] | None = None,
    ) -> None:
        self.id = element_id
        self._displayed = displayed
        self._enabled = enabled
        self._attrs = attrs or {}
        self._ancestors = ancestors or []

    def is_displayed(self) -> bool:
        return self._displayed

    def is_enabled(self) -> bool:
        return self._enabled

    def get_attribute(self, nome: str) -> str:
        return self._attrs.get(nome, "")

    def find_elements(self, _by: str, seletor: str) -> list["FakeElement"]:
        if seletor == "./ancestor-or-self::*[self::button or self::a or @role='button' or self::label]":
            return self._ancestors
        return []


class FakeBrowser:
    def __init__(self, mapping: dict[tuple[str, str], list[FakeElement]]) -> None:
        self.mapping = mapping

    def find_elements(self, by: str, seletor: str) -> list[FakeElement]:
        return list(self.mapping.get((by, seletor), []))


class AcoesNavegadorTest(unittest.TestCase):
    def test_busca_todos_deduplica_elementos_repetidos_por_seletor(self) -> None:
        repetido = FakeElement(element_id="elemento-1")
        unico = FakeElement(element_id="elemento-2")
        navegador = FakeBrowser(
            {
                ("css selector", "tr.vue-item"): [repetido, unico],
                ("css selector", ".vue-item"): [repetido],
            }
        )
        acoes = AcoesNavegador(navegador, logging.getLogger("teste"))

        with patch.dict(
            config.SELETORES,
            {"linhas_tabela_teste": [("css selector", "tr.vue-item"), ("css selector", ".vue-item")]},
            clear=False,
        ):
            elementos = acoes.buscar_todos_por_nome_seletor("linhas_tabela_teste")

        self.assertEqual([elemento.id for elemento in elementos], ["elemento-1", "elemento-2"])

    def test_aguardar_seletor_visivel_ignora_duplicado_oculto(self) -> None:
        oculto = FakeElement(element_id="duplicado-oculto", displayed=False)
        visivel = FakeElement(element_id="duplicado-visivel", displayed=True)
        navegador = FakeBrowser({("id", "readjust_form_value"): [oculto, visivel]})
        acoes = AcoesNavegador(navegador, logging.getLogger("teste"))

        with patch.dict(
            config.SELETORES,
            {"campo_valor_teste": [("id", "readjust_form_value")]},
            clear=False,
        ):
            elemento = acoes.aguardar_seletor(
                "campo_valor_teste", condicao="visivel", timeout=0.1
            )

        self.assertIs(elemento, visivel)


if __name__ == "__main__":
    unittest.main()
