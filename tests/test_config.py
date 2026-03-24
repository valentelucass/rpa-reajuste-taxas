import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import config


class ConfigTest(unittest.TestCase):
    def test_recarrega_configuracoes_a_partir_do_env_da_execucao(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio_temporario:
            caminho_env = Path(diretorio_temporario) / ".env"
            caminho_env.write_text(
                "\n".join(
                    [
                        "EMAIL_LOGIN=teste@example.com",
                        "SENHA_LOGIN=segredo",
                        "URL_LOGIN=https://example.com/login",
                        "HEADLESS=true",
                        "DEBUG_VISUAL=false",
                        "CONFIRMAR_REAJUSTE_FINAL=true",
                        "TIMEOUT=45",
                        "PAGE_LOAD_TIMEOUT=90",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                with patch.object(config, "DIRETORIO_RAIZ", Path(diretorio_temporario)):
                    config.recarregar_configuracoes(sobrescrever_env=True)

                    self.assertEqual(config.EMAIL_LOGIN, "teste@example.com")
                    self.assertEqual(config.SENHA_LOGIN, "segredo")
                    self.assertEqual(config.URL_LOGIN, "https://example.com/login")
                    self.assertTrue(config.MODO_HEADLESS)
                    self.assertFalse(config.DEBUG_VISUAL)
                    self.assertTrue(config.CONFIRMAR_REAJUSTE_FINAL)
                    self.assertEqual(config.TEMPO_ESPERA_PADRAO, 45)
                    self.assertEqual(config.TEMPO_MAXIMO_CARREGAMENTO, 90)

        config.recarregar_configuracoes()


if __name__ == "__main__":
    unittest.main()
