"""==[DOC-FILE]===============================================================
Arquivo : src/paginas/__init__.py
Classe  : -
Pacote  : src.paginas
Modulo  : Paginas - Exposicao

Papel   : Expoe os objetos de pagina usados pelo fluxo Selenium.
[DOC-FILE-END]==============================================================="""

from src.paginas.pagina_login import PaginaLogin
from src.paginas.pagina_tabelas_cliente import PaginaTabelasCliente

__all__ = ["PaginaLogin", "PaginaTabelasCliente"]
