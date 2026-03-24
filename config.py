"""==[DOC-FILE]===============================================================
Arquivo : config.py
Classe  : -
Pacote  : raiz do projeto
Modulo  : Configuracao Central da Automacao

Papel   : Centraliza variaveis editaveis, caminhos de arquivos e seletores da
          interface ESL Cloud, mantendo o fluxo de negocio ajustavel sem tocar
          na logica da automacao.

Conecta com:
- .env - origem dos parametros sensiveis e variaveis de execucao
- src.infraestrutura - consumo de paths, timeouts e flags de navegador
- src.paginas e src.servicos - consumo de rotulos e seletores Selenium

Fluxo geral:
1) Carrega o arquivo `.env` da raiz do projeto.
2) Resolve configuracoes editaveis como URL, credenciais, valor e timeouts.
3) Expoe seletores centralizados para login, filtros, reajuste e paginacao.

Estrutura interna:
Metodos principais:
- carregar_arquivo_env(): injeta valores do `.env` em variaveis de ambiente.
- ler_env_booleano(): converte texto do ambiente para booleano.
[DOC-FILE-END]==============================================================="""

import os

from src.infraestrutura.caminhos import DIRETORIO_APLICACAO

DIRETORIO_RAIZ = DIRETORIO_APLICACAO
DIRETORIO_LOGS = DIRETORIO_RAIZ / "logs"
DIRETORIO_RELATORIOS = DIRETORIO_RAIZ / "reports"
DIRETORIO_SCREENSHOTS = DIRETORIO_RELATORIOS / "screenshots"
ARQUIVO_LOG_PROCESSAMENTO = DIRETORIO_LOGS / "processamento.csv"
ARQUIVO_LOG_ERROS = DIRETORIO_RELATORIOS / "errors.log"
NOME_APLICACAO = "rpa-reajuste-taxas"


def carregar_arquivo_env(sobrescrever: bool = False) -> None:
    caminho_env = DIRETORIO_RAIZ / ".env"
    if not caminho_env.exists():
        return

    for linha_bruta in caminho_env.read_text(encoding="utf-8").splitlines():
        linha = linha_bruta.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue

        chave, valor = linha.split("=", 1)
        chave_limpa = chave.strip()
        valor_limpo = valor.strip().strip('"').strip("'")
        if sobrescrever or chave_limpa not in os.environ:
            os.environ[chave_limpa] = valor_limpo


def ler_env_booleano(nome_variavel: str, valor_padrao: bool) -> bool:
    valor = os.getenv(nome_variavel)
    if valor is None:
        return valor_padrao
    return valor.strip().lower() in {"1", "true", "yes", "sim", "on"}


def recarregar_configuracoes(sobrescrever_env: bool = False) -> None:
    global EMAIL_LOGIN
    global SENHA_LOGIN
    global URL_LOGIN
    global MODO_HEADLESS
    global DEBUG_VISUAL
    global CONFIRMAR_REAJUSTE_FINAL
    global TEMPO_ESPERA_PADRAO
    global TEMPO_MAXIMO_CARREGAMENTO
    global MAX_SCREENSHOTS_ARMAZENADOS
    global MAX_REGISTROS_PROCESSAMENTO
    global MAX_REGISTROS_TRACE
    global MAX_BYTES_LOG_ERROS
    global MAX_BACKUPS_LOG_ERROS

    carregar_arquivo_env(sobrescrever=sobrescrever_env)

    EMAIL_LOGIN = os.getenv("EMAIL_LOGIN", "")
    SENHA_LOGIN = os.getenv("SENHA_LOGIN", "")
    URL_LOGIN = os.getenv("URL_LOGIN", "")
    MODO_HEADLESS = ler_env_booleano("HEADLESS", False)
    DEBUG_VISUAL = ler_env_booleano("DEBUG_VISUAL", False)
    CONFIRMAR_REAJUSTE_FINAL = ler_env_booleano("CONFIRMAR_REAJUSTE_FINAL", False)
    TEMPO_ESPERA_PADRAO = int(os.getenv("TIMEOUT", "30"))
    TEMPO_MAXIMO_CARREGAMENTO = int(os.getenv("PAGE_LOAD_TIMEOUT", "60"))
    MAX_SCREENSHOTS_ARMAZENADOS = int(os.getenv("MAX_SCREENSHOTS_ARMAZENADOS", "40"))
    MAX_REGISTROS_PROCESSAMENTO = int(os.getenv("MAX_REGISTROS_PROCESSAMENTO", "5000"))
    MAX_REGISTROS_TRACE = int(os.getenv("MAX_REGISTROS_TRACE", "1500"))
    MAX_BYTES_LOG_ERROS = int(os.getenv("MAX_BYTES_LOG_ERROS", "1048576"))
    MAX_BACKUPS_LOG_ERROS = int(os.getenv("MAX_BACKUPS_LOG_ERROS", "3"))


recarregar_configuracoes()

CAMINHO_MENUS = (
    "Cadastros",
    "Tabelas de pre\u00e7o",
    "Tabelas de cliente",
)

ROTULOS_FILTROS = {
    "filial_responsavel": "Filial Respons\u00e1vel",
    "ativa": "Ativa",
    "ativa_sim": "Sim",
    "pesquisar": "Pesquisar",
}

ROTULOS_REAJUSTE = {
    "reajuste": "Reajuste",
    "considerar_todos_trechos": "Considerar Todos os trechos",
    "taxa_alvo": "% Taxas adm.",
    "tipo_valor_fixo": "Valor fixo",
    "adicionar": "Adicionar",
    "salvar": "Salvar",
    "confirmar": "Sim",
    "cancelar": "Cancelar",
    "fechar": "Fechar",
}

TEXTOS_SEM_RESULTADO = (
    "Nenhum registro encontrado",
    "Nenhum registro",
    "Nenhum dado encontrado",
)

SELETORES = {
    "campo_email_login": [
        ("id", "user_email"),
        ("css selector", "input[name='user[email]']"),
        ("css selector", "input[type='email']"),
    ],
    "campo_senha_login": [
        ("id", "user_password"),
        ("css selector", "input[name='user[password]']"),
        ("css selector", "input[type='password']"),
    ],
    "botao_entrar": [
        ("css selector", "input[type='submit'][value='Entrar']"),
        ("xpath", "//input[@name='commit' and @value='Entrar']"),
        ("xpath", "//button[normalize-space()='Entrar']"),
    ],
    "linhas_tabela": [
        ("css selector", "tr.vue-item"),
        ("css selector", ".vue-item"),
        ("xpath", "//*[contains(concat(' ', normalize-space(@class), ' '), ' vue-item ')]"),
    ],
    "botao_menu_linha": [
        ("css selector", "button.more-actions"),
        ("xpath", ".//button[contains(@class, 'more-actions')]"),
        ("xpath", ".//button[.//i[contains(@class, 'fa-angle-down')]]"),
    ],
    "botao_proxima_pagina": [
        ("xpath", "//button[.//i[contains(@class, 'fa-angle-right')] and not(@disabled)]"),
        ("css selector", "button:not([disabled]) .fa-angle-right"),
        ("xpath", "//*[contains(@class, 'fa-angle-right') and not(ancestor::button[@disabled])]"),
    ],
    "modal_reajuste": [
        ("id", "price_table_readjustments_modal"),
        ("css selector", "#price_table_readjustments_modal.modal.in"),
        ("xpath", "//*[@id='price_table_readjustments_modal' and not(contains(@style, 'display: none'))]"),
    ],
    "checkbox_considerar_trechos": [
        ("xpath", "//button[.//span[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'considerar todos os trechos')]]"),
        ("xpath", "//span[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'considerar todos os trechos')]/ancestor::button[1]"),
        ("xpath", ".//button[.//span[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'considerar todos os trechos')]]"),
        ("xpath", ".//span[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'considerar todos os trechos')]/ancestor::button[1]"),
    ],
    "campo_taxa_reajuste": [
        ("id", "select2-readjust_form_fee-container"),
        ("xpath", "//span[@id='select2-readjust_form_fee-container']"),
    ],
    "radio_valor_fixo": [
        ("xpath", "//label[@for='readjust_form_value_type_value']"),
        ("id", "readjust_form_value_type_value"),
        ("xpath", "//input[@id='readjust_form_value_type_value']"),
    ],
    "campo_valor_reajuste": [
        ("id", "readjust_form_value"),
        ("css selector", "input[name='readjust_form[value]']"),
    ],
    "botao_adicionar": [
        ("xpath", "//button[@name='add_fee']"),
        ("xpath", "//button[.//span[contains(normalize-space(), 'Adicionar')]]"),
    ],
    "botao_salvar": [
        ("id", "save-btn"),
        ("xpath", "//button[@id='save-btn']"),
        ("xpath", "//button[.//span[contains(normalize-space(), 'Salvar')]]"),
    ],
    "botao_confirmar_swal": [
        ("id", "swal-confirm"),
        ("css selector", "button.swal2-confirm"),
        ("xpath", "//button[normalize-space()='Sim']"),
    ],
    "botao_cancelar_swal": [
        ("id", "swal-cancel"),
        ("css selector", "button.swal2-cancel"),
        ("xpath", "//button[normalize-space()='Cancelar']"),
    ],
    "botao_fechar_modal": [
        ("xpath", "//*[@id='price_table_readjustments_modal']//button[contains(@class, 'close')]"),
        ("xpath", "//*[@id='price_table_readjustments_modal']//button[.//span[contains(normalize-space(), 'Fechar')]]"),
        ("xpath", "//*[@id='price_table_readjustments_modal']//button[normalize-space()='Fechar']"),
        ("css selector", ".modal.show .close"),
        ("xpath", "//button[normalize-space()='Cancelar']"),
        ("xpath", "//button[normalize-space()='Fechar']"),
    ],
    "campo_filial_responsavel": [
        ("xpath", "//select[@id='search_price_tables_corporation_id']/following::span[contains(@class, 'select2-selection')][1]"),
        ("css selector", "#search_price_tables_corporation_id + .select2-container .select2-selection"),
    ],
    "limpar_filial_responsavel": [
        ("xpath", "//select[@id='search_price_tables_corporation_id']/following::span[contains(@class, 'select2-selection__clear')][1]"),
        ("css selector", ".select2-selection__clear"),
    ],
    "campo_ativa": [
        ("xpath", "//select[@id='search_price_tables_active']/following::span[contains(@class, 'select2-selection')][1]"),
        ("css selector", "#search_price_tables_active + .select2-container .select2-selection"),
    ],
    "opcao_ativa_sim": [
        ("xpath", "//li[contains(@class, 'select2-results__option') and normalize-space()='Sim']"),
        ("xpath", "//*[normalize-space()='Sim']"),
    ],
    "botao_pesquisar": [
        ("id", "submit"),
        ("css selector", "button#submit"),
        ("xpath", "//button[@id='submit']"),
    ],
    "informacao_quantidade_registros": [
        ("css selector", ".entries-info"),
        ("xpath", "//*[contains(@class, 'entries-info')]"),
    ],
    "camada_carregamento": [
        ("css selector", ".loading"),
        ("css selector", ".v-overlay--active"),
        ("css selector", ".v-progress-circular"),
        ("css selector", ".spinner-border"),
        ("css selector", ".fa-spinner"),
    ],
}
