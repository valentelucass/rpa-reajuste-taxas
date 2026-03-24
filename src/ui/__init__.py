"""==[DOC-FILE]===============================================================
Arquivo : src/ui/__init__.py
Classe  : -
Pacote  : src.ui
Modulo  : UI - Pacote

Papel   : Marca a pasta da interface desktop como pacote Python sem importar
          dependencias pesadas em tempo de importacao.

Conecta com:
- src.ui.componentes
- src.ui.logger
- src.ui.rpa_worker
- src.ui.ui_main

Fluxo geral:
1) Define `src.ui` como pacote.
2) Evita imports imediatos de PySide6 para nao acoplar a interface ao backend.

Estrutura interna:
Modulos principais:
- componentes
- logger
- rpa_worker
- ui_main
[DOC-FILE-END]==============================================================="""

__all__ = []
