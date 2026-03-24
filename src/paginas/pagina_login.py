"""==[DOC-FILE]===============================================================
Arquivo : src/paginas/pagina_login.py
Classe  : PaginaLogin (class)
Pacote  : src.paginas
Modulo  : Paginas - Login da Plataforma

Papel   : Representa a pagina de autenticacao da ESL Cloud e concentra o fluxo
          de abertura da URL, preenchimento de credenciais e submissao.

Conecta com:
- config - URL e credenciais vindas do `.env`
- src.infraestrutura.acoes_navegador - waits e digitacao segura

Fluxo geral:
1) Abre a URL de login.
2) Aguarda carregamento completo da pagina.
3) Preenche e-mail, senha e clica em Entrar.

Estrutura interna:
Metodos principais:
- abrir(): abre a pagina de login.
- fazer_login(): executa a autenticacao com as credenciais configuradas.
[DOC-FILE-END]==============================================================="""

import config
from src.infraestrutura.acoes_navegador import AcoesNavegador


class PaginaLogin:
    def __init__(self, acoes_navegador: AcoesNavegador) -> None:
        self.acoes_navegador = acoes_navegador

    def abrir(self) -> None:
        self.acoes_navegador.navegador.get(config.URL_LOGIN)
        self.acoes_navegador.aguardar_documento_pronto()
        self.acoes_navegador.aguardar_carregamento_finalizar()

    def fazer_login(self) -> None:
        campo_email = self.acoes_navegador.aguardar_seletor(
            "campo_email_login", condicao="visivel"
        )
        campo_senha = self.acoes_navegador.aguardar_seletor(
            "campo_senha_login", condicao="visivel"
        )
        botao_entrar = self.acoes_navegador.aguardar_seletor(
            "botao_entrar", condicao="clicavel"
        )

        self.acoes_navegador.limpar_e_digitar(campo_email, config.EMAIL_LOGIN)
        self.acoes_navegador.limpar_e_digitar(campo_senha, config.SENHA_LOGIN)
        self.acoes_navegador.clicar_com_seguranca(botao_entrar)
        self.acoes_navegador.aguardar_documento_pronto()
        self.acoes_navegador.aguardar_carregamento_finalizar()
