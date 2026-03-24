import unittest
from pathlib import Path
from unittest.mock import patch

from src.infraestrutura import caminhos


class CaminhosTest(unittest.TestCase):
    def test_resolve_diretorios_do_bundle_quando_rodando_empacotado(self) -> None:
        with patch.object(caminhos.sys, "frozen", True, create=True):
            with patch.object(
                caminhos.sys,
                "executable",
                r"C:\pacote\RPA-Tabela-cliente.exe",
                create=True,
            ):
                with patch.object(
                    caminhos.sys,
                    "_MEIPASS",
                    r"C:\pacote\_internal",
                    create=True,
                ):
                    self.assertEqual(
                        caminhos.resolver_diretorio_aplicacao(),
                        Path(r"C:\pacote"),
                    )
                    self.assertEqual(
                        caminhos.resolver_diretorio_recursos(),
                        Path(r"C:\pacote\_internal"),
                    )
                    self.assertEqual(
                        caminhos.resolver_caminho_recurso("public", "logo.png"),
                        Path(r"C:\pacote\_internal\public\logo.png"),
                    )


if __name__ == "__main__":
    unittest.main()
