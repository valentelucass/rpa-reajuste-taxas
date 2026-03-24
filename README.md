# Painel de Automacao RPA

Aplicacao desktop em Python para controlar e monitorar o robo de reajuste de taxas da plataforma ESL Cloud da Rodogarcia.

## Visao geral

O projeto foi organizado para manter a raiz limpa e concentrar a implementacao dentro de `src/`.

Partes principais:

- `main.py`: bootstrap da aplicacao desktop.
- `config.py`: configuracoes, seletores e paths centralizados.
- `src/ui`: interface desktop em PySide6.
- `src/aplicacao`: orquestracao principal do robo.
- `src/paginas`: login, filtros, leitura da tabela e paginacao.
- `src/servicos`: reajuste, loop da tabela e tratamento de falhas.
- `src/infraestrutura`: Selenium, navegador, logger tecnico e arquivos auxiliares.
- `src/monitoramento`: contexto de execucao e contrato do observador.

O fluxo operacional oficial da automacao esta em `docs/fluxo.md`.

## Estrutura do projeto

```text
.
|-- main.py
|-- config.py
|-- requirements.txt
|-- README.md
|-- .env
|-- .env.example
|-- docs/
|   `-- fluxo.md
|-- logs/
|   `-- processamento.csv
|-- reports/
|   |-- errors.log
|   `-- screenshots/
`-- src/
    |-- aplicacao/
    |-- infraestrutura/
    |-- monitoramento/
    |-- paginas/
    `-- ui/
```

## Estrutura da UI

A interface desktop agora fica totalmente dentro de `src/ui/`:

- `src/ui/ui_main.py`: janela principal do dashboard.
- `src/ui/rpa_worker.py`: thread do Qt que executa o robo.
- `src/ui/logger.py`: estado, estatisticas e registros exibidos no painel.
- `src/ui/componentes.py`: badges, cards e componentes visuais reutilizaveis.

## Convencoes adotadas

- A raiz do projeto deve ficar enxuta.
- A implementacao principal fica dentro de `src/`.
- Cada arquivo Python relevante possui bloco `DOC-FILE` no topo.
- Credenciais e parametros sensiveis ficam no `.env`, nunca no codigo.

## Requisitos

Antes de executar, garanta:

- Python 3.11 ou superior instalado.
- Google Chrome ou Microsoft Edge instalado.
- Acesso a internet e acesso a plataforma ESL Cloud.
- Permissao para gravar arquivos em `logs/` e `reports/`.

Observacao:

- O executavel gerado pelo PyInstaller ja leva o runtime do Python junto.
- O Selenium 4 normalmente resolve o driver automaticamente.

## Preparacao do ambiente

### 1. Entrar na pasta do projeto

```powershell
cd C:\Users\lucas\OneDrive\Desktop\PROJETOS\ESTAGIO\rpa-taxa-combustivel
```

### 2. Criar e ativar ambiente virtual

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se a politica do PowerShell bloquear:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

## Configuracao do `.env`

O projeto le configuracoes da raiz pelo arquivo `.env`.

Modelo esperado:

```env
EMAIL_LOGIN=
SENHA_LOGIN=
URL_LOGIN=
VALOR_REAJUSTE=15
HEADLESS=false
DEBUG_VISUAL=false
CONFIRMAR_REAJUSTE_FINAL=false
TIMEOUT=30
PAGE_LOAD_TIMEOUT=60
```

Descricao:

- `EMAIL_LOGIN`: email da plataforma.
- `SENHA_LOGIN`: senha da plataforma.
- `URL_LOGIN`: URL da tela de login.
- `VALOR_REAJUSTE`: valor fixo aplicado no reajuste.
- `HEADLESS`: `true` ou `false`.
- `DEBUG_VISUAL`: `true` destaca cliques e digitacao em vermelho na tela durante a automacao.
- `CONFIRMAR_REAJUSTE_FINAL`: `true` clica em `Sim` no SweetAlert e executa o reajuste real; `false` roda em modo seguro e nao confirma.
- `TIMEOUT`: timeout padrao das esperas explicitas.
- `PAGE_LOAD_TIMEOUT`: timeout maximo de carregamento.

Recomendacao:

- Em testes e ajuste de seletor, use `HEADLESS=false`.
- Para acompanhar visualmente cada clique em vermelho, use `DEBUG_VISUAL=true`.
- Para validar o fluxo sem aplicar reajustes reais, use `CONFIRMAR_REAJUSTE_FINAL=false`.
- Para producao, use `CONFIRMAR_REAJUSTE_FINAL=true`.
- Em execucao sem acompanhamento visual, use `HEADLESS=true` somente depois de validar o fluxo.

## Como iniciar a interface

**IMPORTANTE:** PySide6 requer Python 3.12 ou 3.13. Python 3.14 ainda não é suportado.

Se você tem múltiplas versões instaladas:

```powershell
py -3.12 main.py
```

Se tiver apenas Python 3.12:

```powershell
python main.py
```

Ao abrir corretamente:

- a janela `Painel de Automacao RPA` sera exibida
- o status inicial sera `Parado`
- os cards iniciam zerados
- a tabela de logs inicia vazia

## Como usar a interface

### Iniciar automacao

1. Abra a interface com `py -3.12 main.py`.
2. Clique em `Iniciar Automacao`.
3. O status muda para `Executando`.
4. A thread do Qt inicia o robo sem travar a interface.
5. O painel passa a atualizar:
   - total de registros
   - processados
   - sucessos
   - falhas
   - progresso
   - logs por linha

### Parar automacao

1. Clique em `Parar Automacao`.
2. O sistema registra a solicitacao de parada.
3. O robo conclui a etapa atual e interrompe de forma controlada.
4. O status volta para `Parado`.

### Reprocessar falhas

Quando uma linha falha:

- ela aparece na tabela com status `Erro`
- o botao `Reprocessar` fica disponivel

Para usar:

1. Aguarde a execucao atual terminar.
2. Clique em `Reprocessar` na linha desejada.
3. O robo executa uma nova tentativa focada naquele registro.

## Fluxo completo

O fluxo oficial detalhado continua em `docs/fluxo.md`, mas o comportamento implementado hoje e este:

### Fase 1: Login

1. Abre `URL_LOGIN`.
2. Aguarda a pagina carregar completamente.
3. Preenche email e senha do `.env`.
4. Clica em `Entrar`.

### Fase 2: Navegacao inicial

1. Clica em `Cadastros`.
2. Clica em `Tabelas de preco`.
3. Clica em `Tabelas de cliente`.

### Fase 3: Preparacao dos filtros

1. Remove a filial pre-selecionada em `Filial Responsavel`, se existir.
2. Abre o filtro `Ativa`.
3. Seleciona `Sim`.
4. Clica em `Pesquisar`.
5. Aguarda a tabela renderizar.

### Fase 4: Leitura da pagina atual

1. Le todas as linhas visiveis da tabela principal.
2. Nao assume quantidade fixa.
3. Hoje a tabela validada no ambiente real abriu com 18 linhas por pagina e a ultima pagina com 7 linhas, mas o codigo trata isso dinamicamente.

### Fase 5: Fluxo por linha

Para cada linha da pagina atual, o robo faz:

1. Abre o menu de acoes da linha.
2. Clica em `Reajuste`.
3. Aguarda o modal `Reajuste de tabela de preco`.
4. Marca `Considerar Todos os trechos`.
5. Abre o Select2 de taxa.
6. Seleciona `% Taxas adm.`.
7. Marca `Valor fixo`.
8. Preenche `VALOR_REAJUSTE`.
9. Clica em `Adicionar`.
10. Clica em `Salvar`.
11. Trata a confirmacao final:
   - `CONFIRMAR_REAJUSTE_FINAL=true`: clica em `Sim` e grava o reajuste.
   - `CONFIRMAR_REAJUSTE_FINAL=false`: nao confirma, cancela o SweetAlert e fecha o modal para validar o loop sem gravar.
12. Aguarda o modal fechar.
13. Volta para a tabela e segue para a proxima linha.

### Fase 6: Troca de pagina

1. Quando termina a ultima linha da pagina atual, o robo procura o botao de proxima pagina (`fa-angle-right`).
2. Se existir e estiver clicavel, avanca para a proxima pagina.
3. Aguarda a nova tabela carregar.
4. Reinicia o loop da Fase 4.

### Fase 7: Encerramento

1. Quando nao existe mais proxima pagina, o robo encerra o processamento.
2. O status volta para parado.
3. A interface fica pronta para uma nova execucao.

### Tratamento de erro durante o fluxo

1. Se uma linha falhar, o robo registra erro no CSV.
2. Tenta gerar screenshot em `reports/screenshots/`.
3. Registra detalhes tecnicos em `reports/errors.log`.
4. Tenta recuperar a interface.
5. Continua para a proxima linha sem abortar a execucao inteira.

### Modo visual

Com `DEBUG_VISUAL=true`, a automacao destaca em vermelho:

1. Cliques em botoes e menus.
2. Campos antes da digitacao.
3. O ponto exato do clique com pulso visual.

## Logs e artefatos

### Log funcional

- `logs/processamento.csv`

Uso:

- sucesso e falha por linha
- rastreabilidade operacional

### Log tecnico

- `reports/errors.log`

Uso:

- stack trace
- falhas tecnicas
- diagnostico de execucao

### Screenshots de erro

- `reports/screenshots/`

Uso:

- evidencia visual da tela no momento da falha

## Primeira execucao recomendada

1. Configure `HEADLESS=false`.
2. Rode `py -3.12 main.py`.
3. Clique em `Iniciar Automacao`.
4. Observe os primeiros reajustes.
5. Verifique `logs/processamento.csv`.
6. Verifique `reports/errors.log`.
7. Se necessario, ajuste seletores em `config.py`.

## Solucao de problemas

### `ModuleNotFoundError: No module named 'PySide6'`

```powershell
pip install -r requirements.txt
```

### `ModuleNotFoundError: No module named 'selenium'`

```powershell
pip install -r requirements.txt
```

### O navegador nao abre

Verifique:

- se Google Chrome ou Microsoft Edge estao instalados
- se o ambiente permite baixar ou usar o driver automaticamente
- se antivirus ou politica local esta bloqueando o navegador

### O robo falha no login

Verifique:

- `EMAIL_LOGIN`
- `SENHA_LOGIN`
- `URL_LOGIN`
- possiveis mudancas na tela de login

### O robo nao encontra botoes ou campos

Verifique:

- mudancas no HTML da plataforma
- seletores em `config.py`
- aderencia ao fluxo em `docs/fluxo.md`

### A execucao falha no meio

Consulte:

- `logs/processamento.csv`
- `reports/errors.log`
- `reports/screenshots/`

## Comandos uteis

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Rodar a interface:

```powershell
py -3.12 main.py
```

Validar sintaxe:

```powershell
python -m compileall .
```

## Observacoes finais

- `docs/fluxo.md` esta no `.gitignore`, entao pode permanecer local sem versionamento.
- Em manutencao, comece pelos blocos `DOC-FILE` no topo dos arquivos Python.
- A raiz deve permanecer enxuta; novas implementacoes devem entrar em `src/`.
