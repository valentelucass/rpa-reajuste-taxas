"""==[DOC-FILE]===============================================================
Arquivo : src/ui/ui_main.py
Classe  : JanelaPainelAutomacao (class)
Pacote  : src.ui
Modulo  : UI - Janela Principal

Papel   : Monta o dashboard desktop do RPA, concentrando layout, estilizacao
          e reacao aos sinais emitidos pela thread de execucao.

Conecta com:
- src.ui.componentes - cards e badges reutilizaveis
- src.ui.rpa_worker - thread que executa o robo
- PySide6.QtWidgets - elementos da interface visual

Fluxo geral:
1) Monta o cabecalho com branding da empresa.
2) Inicia e encerra a thread da automacao sem bloquear o Qt.
3) Atualiza indicadores, progresso e historico em tempo real.
4) Permite reprocessar registros com falha apos a execucao.

Estrutura interna:
Metodos principais:
- iniciar_automacao(): dispara o fluxo completo do robo.
- parar_automacao(): solicita interrupcao controlada.
- reprocessar_registro(): dispara reprocessamento isolado.
- limpar_painel(): limpa tabela e indicadores para nova execucao.
[DOC-FILE-END]==============================================================="""

from datetime import datetime
from functools import partial

import config
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.infraestrutura.caminhos import resolver_caminho_recurso
from src.ui.componentes import PALETA_CORES, CartaoEstatistica, EtiquetaStatus
from src.ui.rpa_worker import TrabalhadorExecucaoRpa

LINHAS_LOGS_POR_PAGINA = 8
ALTURA_LINHA_LOG = 60
ALTURA_CABECALHO_TABELA_LOG = 44
LARGURA_COLUNA_LOG_LINHA = 92
LARGURA_COLUNA_LOG_CLIENTE = 240
LARGURA_COLUNA_LOG_STATUS = 156
LARGURA_COLUNA_LOG_HORARIO = 112
LARGURA_COLUNA_LOG_ACAO = 136


class JanelaPainelAutomacao(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.trabalhador_atual: TrabalhadorExecucaoRpa | None = None
        self.registros_logs: list[dict] = []
        self.total_logs = 0
        self.total_logs_reprocessaveis = 0
        self.indice_pagina_logs = 0
        self.linhas_por_pagina_logs = LINHAS_LOGS_POR_PAGINA
        self.reprocessamento_habilitado = True
        self.fonte_mono = QFont("Consolas", 10)
        self.fonte_mono.setStyleHint(QFont.Monospace)

        self.setWindowTitle(f"Rodogarcia | {config.NOME_APLICACAO}")
        self.resize(1450, 960)
        self.setMinimumSize(1240, 820)
        self._aplicar_estilo_global()
        self._montar_interface()
        self._atualizar_status_robo("Parado")
        self._atualizar_estatisticas(
            {"total_registros": 0, "processados": 0, "sucessos": 0, "falhas": 0}
        )
        self._atualizar_progresso({"atual": 0, "total": 0, "percentual": 0})
        self._atualizar_resumo_logs()
        self._renderizar_pagina_logs()

    def _montar_interface(self) -> None:
        scroll_area = QScrollArea()
        scroll_area.setObjectName("scrollPrincipal")
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll_area)

        widget_central = QWidget()
        widget_central.setObjectName("widgetCentral")
        scroll_area.setWidget(widget_central)
        self.scroll_area = scroll_area
        self.widget_central = widget_central

        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(30, 26, 30, 26)
        layout_principal.setSpacing(20)
        self.layout_principal = layout_principal

        layout_principal.addWidget(self._criar_cabecalho())
        layout_principal.addWidget(self._criar_secao_controles())
        layout_principal.addLayout(self._criar_grade_estatisticas())
        layout_principal.addWidget(self._criar_secao_progresso())
        layout_principal.addWidget(self._criar_secao_logs(), 1)
        layout_principal.addWidget(self._criar_rodape())

    def _criar_cabecalho(self) -> QFrame:
        cartao = QFrame()
        cartao.setObjectName("cabecalhoPainel")
        self._aplicar_sombra(cartao, blur=34, deslocamento_y=10)

        layout = QHBoxLayout(cartao)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(24)

        marca = QWidget()
        layout_marca = QHBoxLayout(marca)
        layout_marca.setContentsMargins(0, 0, 0, 0)
        layout_marca.setSpacing(18)

        rotulo_logo = QLabel()
        pixmap_logo = self._obter_logo_empresa()
        if pixmap_logo is not None:
            rotulo_logo.setPixmap(
                pixmap_logo.scaledToHeight(48, Qt.SmoothTransformation)
            )
        else:
            rotulo_logo.setObjectName("logoFallback")
            rotulo_logo.setText("Rodogarcia")
        layout_marca.addWidget(rotulo_logo, alignment=Qt.AlignVCenter)

        divisor = QFrame()
        divisor.setFixedWidth(1)
        divisor.setStyleSheet(
            f"background: {PALETA_CORES['borda_forte']}; border: none;"
        )
        layout_marca.addWidget(divisor)

        bloco_titulo = QVBoxLayout()
        bloco_titulo.setSpacing(6)

        selo = QLabel(config.NOME_APLICACAO)
        selo.setObjectName("etiquetaTopo")
        titulo = QLabel("Reajuste de Taxas")
        titulo.setStyleSheet(
            f"color: {PALETA_CORES['texto_padrao']}; font-size: 28px; font-weight: 800;"
        )
        subtitulo = QLabel(
            f"Painel operacional do projeto {config.NOME_APLICACAO} com historico de execucao em tempo real."
        )
        subtitulo.setStyleSheet(
            f"color: {PALETA_CORES['texto_mutado']}; font-size: 13px;"
        )
        bloco_titulo.addWidget(selo, alignment=Qt.AlignLeft)
        bloco_titulo.addWidget(titulo)
        bloco_titulo.addWidget(subtitulo)
        layout_marca.addLayout(bloco_titulo, 1)

        layout.addWidget(marca, 1)

        painel_status = QFrame()
        painel_status.setObjectName("cabecalhoStatus")
        painel_status.setMinimumWidth(300)

        layout_status = QVBoxLayout(painel_status)
        layout_status.setContentsMargins(18, 18, 18, 18)
        layout_status.setSpacing(8)

        rotulo_status = QLabel("Status do robo")
        rotulo_status.setStyleSheet(
            f"color: {PALETA_CORES['texto_mutado']}; font-size: 12px; font-weight: 600;"
        )
        self.etiqueta_status = EtiquetaStatus("Parado")
        self.rotulo_status_detalhe = QLabel("Aguardando nova execucao.")
        self.rotulo_status_detalhe.setStyleSheet(
            f"color: {PALETA_CORES['texto_padrao']}; font-size: 13px; font-weight: 600;"
        )
        self.rotulo_status_horario = QLabel("Ultima atualizacao: --:--:--")
        self.rotulo_status_horario.setStyleSheet(
            f"color: {PALETA_CORES['texto_mutado']}; font-size: 12px;"
        )

        layout_status.addWidget(rotulo_status)
        layout_status.addWidget(self.etiqueta_status, alignment=Qt.AlignLeft)
        layout_status.addWidget(self.rotulo_status_detalhe)
        layout_status.addWidget(self.rotulo_status_horario)

        layout.addWidget(painel_status, alignment=Qt.AlignTop)
        return cartao

    def _criar_secao_controles(self) -> QFrame:
        cartao = QFrame()
        cartao.setObjectName("cartaoPadrao")
        self._aplicar_sombra(cartao, blur=24, deslocamento_y=5)

        layout = QHBoxLayout(cartao)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(18)

        descricao = QVBoxLayout()
        descricao.setSpacing(6)
        titulo = QLabel("Controles de execucao")
        titulo.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {PALETA_CORES['texto_padrao']};"
        )
        texto = QLabel(
            "Inicie uma rodada completa, interrompa com seguranca e acompanhe o estado do robo sem bloquear a interface."
        )
        texto.setWordWrap(True)
        texto.setStyleSheet(
            f"font-size: 13px; color: {PALETA_CORES['texto_mutado']};"
        )
        self.rotulo_contexto_operacao = QLabel(
            "Pronto para iniciar uma nova rodada de processamento."
        )
        self.rotulo_contexto_operacao.setStyleSheet(
            f"font-size: 12px; color: {PALETA_CORES['primaria']}; font-weight: 600;"
        )
        descricao.addWidget(titulo)
        descricao.addWidget(texto)
        descricao.addWidget(self.rotulo_contexto_operacao)
        layout.addLayout(descricao, 1)

        bloco_botoes = QHBoxLayout()
        bloco_botoes.setSpacing(12)

        bloco_valor = QVBoxLayout()
        bloco_valor.setSpacing(4)
        rotulo_valor = QLabel("Valor do reajuste")
        rotulo_valor.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {PALETA_CORES['texto_mutado']};"
        )
        self.input_valor_reajuste = QLineEdit("15")
        self.input_valor_reajuste.setFixedWidth(120)
        self.input_valor_reajuste.setFixedHeight(38)
        self.input_valor_reajuste.setPlaceholderText("Ex: 15")
        self.input_valor_reajuste.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {PALETA_CORES.get('fundo_card', '#FFFFFF')};
                border: 1px solid {PALETA_CORES['borda']};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                font-weight: 600;
                color: {PALETA_CORES['texto_padrao']};
            }}
            QLineEdit:focus {{
                border-color: {PALETA_CORES['primaria']};
            }}
            """
        )
        bloco_valor.addWidget(rotulo_valor)
        bloco_valor.addWidget(self.input_valor_reajuste)
        bloco_botoes.addLayout(bloco_valor)

        self.botao_iniciar = QPushButton("Iniciar execucao")
        self.botao_iniciar.setObjectName("botaoPrimario")
        self.botao_iniciar.setCursor(Qt.PointingHandCursor)
        self.botao_iniciar.clicked.connect(self.iniciar_automacao)

        self.botao_parar = QPushButton("Parar execucao")
        self.botao_parar.setObjectName("botaoPerigo")
        self.botao_parar.setCursor(Qt.PointingHandCursor)
        self.botao_parar.clicked.connect(self.parar_automacao)
        self.botao_parar.setEnabled(False)

        bloco_botoes.addSpacing(24)
        bloco_botoes.addWidget(self.botao_iniciar, alignment=Qt.AlignBottom)
        bloco_botoes.addWidget(self.botao_parar, alignment=Qt.AlignBottom)
        layout.addLayout(bloco_botoes)
        return cartao

    def _criar_grade_estatisticas(self) -> QGridLayout:
        grade = QGridLayout()
        grade.setSpacing(18)

        self.cartao_total = CartaoEstatistica(
            "Total de registros",
            PALETA_CORES["primaria"],
        )
        self.cartao_processados = CartaoEstatistica(
            "Processados",
            PALETA_CORES["secundaria"],
        )
        self.cartao_sucessos = CartaoEstatistica(
            "Sucessos",
            PALETA_CORES["sucesso"],
        )
        self.cartao_falhas = CartaoEstatistica(
            "Falhas",
            PALETA_CORES["perigo"],
        )

        grade.addWidget(self.cartao_total, 0, 0)
        grade.addWidget(self.cartao_processados, 0, 1)
        grade.addWidget(self.cartao_sucessos, 0, 2)
        grade.addWidget(self.cartao_falhas, 0, 3)

        for indice in range(4):
            grade.setColumnStretch(indice, 1)

        return grade

    def _criar_secao_progresso(self) -> QFrame:
        cartao = QFrame()
        cartao.setObjectName("cartaoPadrao")
        self._aplicar_sombra(cartao, blur=24, deslocamento_y=5)

        layout = QVBoxLayout(cartao)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        topo = QHBoxLayout()
        topo.setSpacing(18)

        bloco_texto = QVBoxLayout()
        bloco_texto.setSpacing(6)
        titulo = QLabel("Progresso da automacao")
        titulo.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {PALETA_CORES['texto_padrao']};"
        )
        self.rotulo_progresso = QLabel("Aguardando inicio da automacao")
        self.rotulo_progresso.setStyleSheet(
            f"font-size: 13px; color: {PALETA_CORES['texto_mutado']};"
        )
        bloco_texto.addWidget(titulo)
        bloco_texto.addWidget(self.rotulo_progresso)
        topo.addLayout(bloco_texto)
        topo.addStretch(1)

        self.rotulo_percentual = QLabel("0%")
        self.rotulo_percentual.setObjectName("rotuloPercentual")
        topo.addWidget(self.rotulo_percentual)

        self.barra_progresso = QProgressBar()
        self.barra_progresso.setRange(0, 100)
        self.barra_progresso.setValue(0)
        self.barra_progresso.setTextVisible(False)
        self.barra_progresso.setFixedHeight(14)
        self.barra_progresso.setObjectName("barraProgresso")

        layout.addLayout(topo)
        layout.addWidget(self.barra_progresso)
        return cartao

    def _criar_secao_logs(self) -> QFrame:
        cartao = QFrame()
        cartao.setObjectName("cartaoPadrao")
        cartao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._aplicar_sombra(cartao, blur=24, deslocamento_y=5)
        self.cartao_logs = cartao

        layout = QVBoxLayout(cartao)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        cabecalho = QHBoxLayout()
        cabecalho.setSpacing(18)

        bloco_titulos = QVBoxLayout()
        bloco_titulos.setSpacing(6)
        titulo = QLabel("Historico de execucao")
        titulo.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {PALETA_CORES['texto_padrao']};"
        )
        subtitulo = QLabel(
            "Eventos operacionais, erros e reprocessamentos organizados em uma grade de leitura continua."
        )
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet(
            f"font-size: 13px; color: {PALETA_CORES['texto_mutado']};"
        )
        bloco_titulos.addWidget(titulo)
        bloco_titulos.addWidget(subtitulo)
        cabecalho.addLayout(bloco_titulos, 1)

        layout.addLayout(cabecalho)

        resumo_logs = QHBoxLayout()
        resumo_logs.setSpacing(12)

        cartao_eventos, self.rotulo_total_logs, self.rotulo_total_logs_detalhe = (
            self._criar_cartao_resumo_log("Eventos", "0", "linhas registradas")
        )
        cartao_reprocessar, self.rotulo_reprocessaveis, self.rotulo_reprocessaveis_detalhe = (
            self._criar_cartao_resumo_log(
                "Reprocessaveis",
                "0",
                "falhas elegiveis para nova tentativa",
            )
        )
        cartao_ultimo_evento, self.rotulo_ultimo_evento, self.rotulo_ultimo_evento_detalhe = (
            self._criar_cartao_resumo_log("Ultimo evento", "Aguardando", "sem atividade")
        )

        resumo_logs.addWidget(cartao_eventos)
        resumo_logs.addWidget(cartao_reprocessar)
        resumo_logs.addWidget(cartao_ultimo_evento)
        layout.addLayout(resumo_logs)

        container_tabela = QFrame()
        container_tabela.setObjectName("containerTabelaLogs")
        container_tabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        container_layout = QVBoxLayout(container_tabela)
        container_layout.setContentsMargins(8, 8, 8, 8)
        self.container_tabela_logs = container_tabela

        self.tabela_logs = QTableWidget(0, 6)
        self.tabela_logs.setObjectName("tabelaLogs")
        self.tabela_logs.setHorizontalHeaderLabels(
            ["Linha", "Cliente", "Status", "Detalhe", "Horario", "Acao"]
        )
        self.tabela_logs.verticalHeader().setVisible(False)
        self.tabela_logs.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabela_logs.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela_logs.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela_logs.setFocusPolicy(Qt.NoFocus)
        self.tabela_logs.setWordWrap(False)
        self.tabela_logs.setTextElideMode(Qt.ElideRight)
        self.tabela_logs.setShowGrid(False)
        self.tabela_logs.setAlternatingRowColors(False)
        self.tabela_logs.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tabela_logs.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tabela_logs.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabela_logs.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabela_logs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        cabecalho = self.tabela_logs.horizontalHeader()
        cabecalho.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cabecalho.setHighlightSections(False)
        cabecalho.setSectionResizeMode(0, QHeaderView.Fixed)
        cabecalho.setSectionResizeMode(1, QHeaderView.Fixed)
        cabecalho.setSectionResizeMode(2, QHeaderView.Fixed)
        cabecalho.setSectionResizeMode(3, QHeaderView.Stretch)
        cabecalho.setSectionResizeMode(4, QHeaderView.Fixed)
        cabecalho.setSectionResizeMode(5, QHeaderView.Fixed)
        cabecalho.setFixedHeight(44)
        self.tabela_logs.setColumnWidth(0, LARGURA_COLUNA_LOG_LINHA)
        self.tabela_logs.setColumnWidth(1, LARGURA_COLUNA_LOG_CLIENTE)
        self.tabela_logs.setColumnWidth(2, LARGURA_COLUNA_LOG_STATUS)
        self.tabela_logs.setColumnWidth(4, LARGURA_COLUNA_LOG_HORARIO)
        self.tabela_logs.setColumnWidth(5, LARGURA_COLUNA_LOG_ACAO)

        self.tabela_logs.verticalHeader().setDefaultSectionSize(ALTURA_LINHA_LOG)
        self.tabela_logs.verticalScrollBar().setSingleStep(24)
        self._ajustar_altura_tabela_logs()
        container_layout.addWidget(self.tabela_logs)
        layout.addWidget(container_tabela)

        paginacao = QHBoxLayout()
        paginacao.setSpacing(10)

        self.rotulo_contagem_logs = QLabel("Mostrando 0-0 de 0 registros")
        self.rotulo_contagem_logs.setObjectName("rotuloPaginacaoLogs")
        paginacao.addWidget(self.rotulo_contagem_logs)
        paginacao.addStretch(1)

        self.botao_pagina_anterior_logs = QPushButton("<")
        self.botao_pagina_anterior_logs.setObjectName("botaoPaginacao")
        self.botao_pagina_anterior_logs.setCursor(Qt.PointingHandCursor)
        self.botao_pagina_anterior_logs.clicked.connect(
            self._ir_para_pagina_logs_anterior
        )
        paginacao.addWidget(self.botao_pagina_anterior_logs)

        self.rotulo_pagina_logs = QLabel("Pagina 1 de 1")
        self.rotulo_pagina_logs.setObjectName("rotuloPaginacaoLogs")
        paginacao.addWidget(self.rotulo_pagina_logs)

        self.botao_pagina_seguinte_logs = QPushButton(">")
        self.botao_pagina_seguinte_logs.setObjectName("botaoPaginacao")
        self.botao_pagina_seguinte_logs.setCursor(Qt.PointingHandCursor)
        self.botao_pagina_seguinte_logs.clicked.connect(
            self._ir_para_pagina_logs_seguinte
        )
        paginacao.addWidget(self.botao_pagina_seguinte_logs)

        layout.addLayout(paginacao)
        return cartao

    def _criar_rodape(self) -> QFrame:
        rodape = QFrame()
        rodape.setObjectName("rodapePainel")

        layout = QHBoxLayout(rodape)
        layout.setContentsMargins(4, 14, 4, 0)
        layout.setSpacing(24)

        bloco_esquerdo = QWidget()
        layout_esquerdo = QVBoxLayout(bloco_esquerdo)
        layout_esquerdo.setContentsMargins(0, 0, 0, 0)
        layout_esquerdo.setSpacing(4)

        titulo = QLabel("RPA REAJUSTE TABELAS VIGENCIA")
        titulo.setObjectName("rodapeTitulo")
        descricao = QLabel(
            "Automacao desktop para copia, vigencia e reajuste de tabelas."
        )
        descricao.setObjectName("rodapeTexto")
        descricao.setWordWrap(True)
        layout_esquerdo.addWidget(titulo)
        layout_esquerdo.addWidget(descricao)

        bloco_direito = QWidget()
        bloco_direito.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        layout_direito = QVBoxLayout(bloco_direito)
        layout_direito.setContentsMargins(0, 0, 0, 0)
        layout_direito.setSpacing(4)

        linha_autoria = QWidget()
        layout_autoria = QHBoxLayout(linha_autoria)
        layout_autoria.setContentsMargins(0, 0, 0, 0)
        layout_autoria.setSpacing(4)
        layout_autoria.addStretch(1)

        rotulo_autoria = QLabel("Desenvolvido por")
        rotulo_autoria.setObjectName("rodapeTexto")
        link_autoria = QLabel(
            '<a href="https://www.linkedin.com/in/dev-lucasandrade/" '
            'style="color: #21478A; text-decoration: none; font-weight: 700;">'
            "@valentelucass</a>"
        )
        link_autoria.setTextFormat(Qt.RichText)
        link_autoria.setTextInteractionFlags(Qt.TextBrowserInteraction)
        link_autoria.setOpenExternalLinks(True)
        link_autoria.setCursor(Qt.PointingHandCursor)
        layout_autoria.addWidget(rotulo_autoria)
        layout_autoria.addWidget(link_autoria)

        suporte = QLabel("Suporte: lucasmac.dev@gmail.com")
        suporte.setObjectName("rodapeTexto")
        suporte.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout_direito.addWidget(linha_autoria)
        layout_direito.addWidget(suporte)

        layout.addWidget(bloco_esquerdo, 1)
        layout.addWidget(bloco_direito, alignment=Qt.AlignRight | Qt.AlignVCenter)
        return rodape

    def iniciar_automacao(self) -> None:
        if self.trabalhador_atual and self.trabalhador_atual.isRunning():
            return

        texto_valor = self.input_valor_reajuste.text().strip()
        if not texto_valor:
            QMessageBox.warning(
                self,
                "Valor ausente",
                "Informe o valor do reajuste antes de iniciar.",
            )
            return

        try:
            valor_reajuste = float(texto_valor.replace(",", "."))
        except ValueError:
            QMessageBox.warning(
                self,
                "Valor invalido",
                "O valor do reajuste deve ser numerico. Exemplo: 15 ou 27.5",
            )
            return

        self._iniciar_trabalhador("completa", valor_reajuste=valor_reajuste)

    def parar_automacao(self) -> None:
        if self.trabalhador_atual and self.trabalhador_atual.isRunning():
            self.trabalhador_atual.solicitar_parada()

    def reprocessar_registro(self, contexto_registro: dict) -> None:
        if self.trabalhador_atual and self.trabalhador_atual.isRunning():
            QMessageBox.warning(
                self,
                "Execucao em andamento",
                "Aguarde a execucao atual terminar antes de reprocessar um item.",
            )
            return

        texto_valor = self.input_valor_reajuste.text().strip()
        if not texto_valor:
            QMessageBox.warning(
                self,
                "Valor ausente",
                "Informe o valor do reajuste antes de reprocessar.",
            )
            return

        try:
            valor_reajuste = float(texto_valor.replace(",", "."))
        except ValueError:
            QMessageBox.warning(
                self,
                "Valor invalido",
                "O valor do reajuste deve ser numerico. Exemplo: 15 ou 27.5",
            )
            return

        self._iniciar_trabalhador(
            "reprocessamento", contexto_registro, valor_reajuste=valor_reajuste
        )

    def _iniciar_trabalhador(
        self,
        modo_execucao: str,
        contexto_reprocessamento: dict | None = None,
        *,
        valor_reajuste: float,
    ) -> None:
        self.trabalhador_atual = TrabalhadorExecucaoRpa(
            valor_reajuste=valor_reajuste,
            modo_execucao=modo_execucao,
            contexto_reprocessamento=contexto_reprocessamento,
            parent=self,
        )
        self.trabalhador_atual.painel_limpo.connect(self.limpar_painel)
        self.trabalhador_atual.status_alterado.connect(self._atualizar_status_robo)
        self.trabalhador_atual.estatisticas_atualizadas.connect(
            self._atualizar_estatisticas
        )
        self.trabalhador_atual.progresso_atualizado.connect(self._atualizar_progresso)
        self.trabalhador_atual.registro_log_adicionado.connect(
            self._adicionar_registro_log
        )
        self.trabalhador_atual.erro_fatal.connect(self._tratar_erro_fatal)
        self.trabalhador_atual.execucao_encerrada.connect(self._ao_encerrar_execucao)
        self.trabalhador_atual.finished.connect(self._ao_finalizar_thread)

        self.botao_iniciar.setEnabled(False)
        self.botao_parar.setEnabled(True)
        self._habilitar_botoes_reprocessar(False)
        self.trabalhador_atual.start()

    def limpar_painel(self) -> None:
        self.tabela_logs.setRowCount(0)
        self.registros_logs.clear()
        self.total_logs = 0
        self.total_logs_reprocessaveis = 0
        self.indice_pagina_logs = 0
        self._atualizar_estatisticas(
            {"total_registros": 0, "processados": 0, "sucessos": 0, "falhas": 0}
        )
        self._atualizar_progresso({"atual": 0, "total": 0, "percentual": 0})
        self._atualizar_resumo_logs()
        self._renderizar_pagina_logs()

    def _atualizar_status_robo(self, status: str) -> None:
        detalhes = {
            "Parado": (
                "Aguardando nova execucao.",
                "Pronto para iniciar uma rodada completa ou reprocessar falhas.",
            ),
            "Executando": (
                "Robo em atividade.",
                "Acompanhe os eventos na grade abaixo e interrompa se necessario.",
            ),
            "Erro": (
                "Execucao encerrada com erro.",
                "Revise o historico antes de iniciar uma nova tentativa.",
            ),
        }
        detalhe_status, detalhe_controle = detalhes.get(
            status,
            (
                "Estado atualizado.",
                "Painel sincronizado com o andamento atual do robo.",
            ),
        )

        self.etiqueta_status.atualizar(status)
        self.rotulo_status_detalhe.setText(detalhe_status)
        self.rotulo_status_horario.setText(
            f"Ultima atualizacao: {datetime.now().strftime('%H:%M:%S')}"
        )
        self.rotulo_contexto_operacao.setText(detalhe_controle)

    def _atualizar_estatisticas(self, dados: dict) -> None:
        self.cartao_total.atualizar_valor(int(dados.get("total_registros", 0)))
        self.cartao_processados.atualizar_valor(int(dados.get("processados", 0)))
        self.cartao_sucessos.atualizar_valor(int(dados.get("sucessos", 0)))
        self.cartao_falhas.atualizar_valor(int(dados.get("falhas", 0)))

    def _atualizar_progresso(self, dados: dict) -> None:
        atual = int(dados.get("atual", 0))
        total = int(dados.get("total", 0))
        percentual = int(dados.get("percentual", 0))

        if total <= 0:
            self.rotulo_progresso.setText("Aguardando inicio da automacao")
        else:
            self.rotulo_progresso.setText(f"{atual} de {total} registros acompanhados")

        self.rotulo_percentual.setText(f"{percentual}%")
        self.barra_progresso.setValue(percentual)

    def _adicionar_registro_log(self, dados: dict) -> None:
        estava_na_ultima_pagina = (
            not self.registros_logs
            or self.indice_pagina_logs >= self._obter_ultima_pagina_logs()
        )
        cliente = str(dados.get("cliente", "-")).strip() or "-"
        status = str(dados.get("status", "")).strip() or "Parado"
        horario = str(dados.get("horario", "")).strip()
        mensagem_original = str(dados.get("mensagem", "")).strip()
        mensagem = self._normalizar_mensagem_log(mensagem_original) or "Evento registrado."

        registro = {
            "id_linha": str(dados.get("id_linha", "-")),
            "cliente": cliente,
            "status": status,
            "horario": horario,
            "mensagem": mensagem,
            "mensagem_original": mensagem_original or mensagem,
            "pode_reprocessar": bool(dados.get("pode_reprocessar")),
            "contexto": dict(dados),
            "numero_pagina": int(dados.get("numero_pagina", 0) or 0),
            "numero_linha": int(dados.get("numero_linha", 0) or 0),
            "identificador": str(dados.get("identificador", "")).strip(),
            "chave_consolidacao": self._obter_chave_consolidacao_registro(dados),
        }
        indice_existente = self._localizar_indice_registro_existente(
            registro["chave_consolidacao"]
        )

        if indice_existente is None:
            self.registros_logs.append(registro)
            if estava_na_ultima_pagina:
                self.indice_pagina_logs = self._obter_ultima_pagina_logs()
        else:
            self.registros_logs[indice_existente].update(registro)

        self._sincronizar_totais_logs()
        self.indice_pagina_logs = min(
            self.indice_pagina_logs,
            self._obter_ultima_pagina_logs(),
        )

        self._renderizar_pagina_logs()
        self._atualizar_resumo_logs(status=status, horario=horario, mensagem=mensagem)

    def _setar_item_texto(
        self,
        linha: int,
        coluna: int,
        texto: str,
        alinhamento: Qt.AlignmentFlag = Qt.AlignLeft | Qt.AlignVCenter,
        cor: str | None = None,
        fonte: QFont | None = None,
        destaque: bool = False,
        dica: str | None = None,
    ) -> None:
        item = QTableWidgetItem(texto)
        item.setTextAlignment(alinhamento)
        item.setToolTip(dica or texto)

        if cor:
            item.setForeground(QBrush(QColor(cor)))

        if fonte is not None:
            item.setFont(fonte)

        if destaque:
            fonte_item = item.font()
            fonte_item.setBold(True)
            item.setFont(fonte_item)

        self.tabela_logs.setItem(linha, coluna, item)

    def _criar_widget_status_tabela(self, status: str) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        cor_fundo, cor_texto, cor_borda = EtiquetaStatus.MAPA_CORES_STATUS.get(
            status,
            ("#F8FAFC", PALETA_CORES["texto_padrao"], PALETA_CORES["borda"]),
        )

        badge = QFrame()
        badge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        badge.setMinimumWidth(LARGURA_COLUNA_LOG_STATUS - 18)
        badge.setStyleSheet(
            f"""
            QFrame {{
                background-color: {cor_fundo};
                border: 1px solid {cor_borda};
                border-radius: 11px;
            }}
            """
        )
        layout_badge = QHBoxLayout(badge)
        layout_badge.setContentsMargins(12, 6, 12, 6)
        layout_badge.setSpacing(7)

        marcador = QFrame()
        marcador.setFixedSize(8, 8)
        marcador.setStyleSheet(
            f"background-color: {cor_texto}; border: none; border-radius: 4px;"
        )

        rotulo = QLabel(status)
        rotulo.setStyleSheet(
            f"color: {cor_texto}; font-size: 11px; font-weight: 700; border: none;"
        )

        layout_badge.addWidget(marcador, alignment=Qt.AlignVCenter)
        layout_badge.addWidget(rotulo, alignment=Qt.AlignVCenter)
        layout.addWidget(badge)
        return container

    def _criar_widget_acao_tabela(self, botao: QPushButton) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(botao)
        return container

    def _criar_cartao_resumo_log(
        self,
        titulo: str,
        valor: str,
        detalhe: str,
    ) -> tuple[QFrame, QLabel, QLabel]:
        cartao = QFrame()
        cartao.setObjectName("resumoLogCard")
        cartao.setMinimumWidth(180)
        cartao.setMinimumHeight(96)

        layout = QVBoxLayout(cartao)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        rotulo_titulo = QLabel(titulo)
        rotulo_titulo.setStyleSheet(
            f"color: {PALETA_CORES['texto_mutado']}; font-size: 11px; font-weight: 700;"
        )
        rotulo_valor = QLabel(valor)
        rotulo_valor.setMinimumHeight(30)
        rotulo_valor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        rotulo_valor.setStyleSheet(
            f"color: {PALETA_CORES['texto_padrao']}; font-size: 20px; font-weight: 800;"
        )
        rotulo_detalhe = QLabel(detalhe)
        rotulo_detalhe.setWordWrap(True)
        rotulo_detalhe.setStyleSheet(
            f"color: {PALETA_CORES['texto_sutil']}; font-size: 11px;"
        )

        layout.addWidget(rotulo_titulo)
        layout.addWidget(rotulo_valor)
        layout.addWidget(rotulo_detalhe)
        return cartao, rotulo_valor, rotulo_detalhe

    def _atualizar_resumo_logs(
        self,
        status: str | None = None,
        horario: str = "",
        mensagem: str = "",
    ) -> None:
        self.rotulo_total_logs.setText(self._formatar_inteiro(self.total_logs))
        self.rotulo_total_logs_detalhe.setText("linhas registradas")

        self.rotulo_reprocessaveis.setText(
            self._formatar_inteiro(self.total_logs_reprocessaveis)
        )
        self.rotulo_reprocessaveis_detalhe.setText(
            "falhas elegiveis para nova tentativa"
        )

        if status is None:
            self.rotulo_ultimo_evento.setText("Aguardando")
            self.rotulo_ultimo_evento_detalhe.setText("sem atividade")
            return

        self.rotulo_ultimo_evento.setText(status)
        if horario or mensagem:
            resumo = self._resumir_texto(mensagem, 52)
            partes = [parte for parte in (horario, resumo) if parte]
            self.rotulo_ultimo_evento_detalhe.setText(" | ".join(partes))
        else:
            self.rotulo_ultimo_evento_detalhe.setText("evento sincronizado")

    def _habilitar_botoes_reprocessar(self, habilitado: bool) -> None:
        self.reprocessamento_habilitado = habilitado
        self._renderizar_pagina_logs()

    def _ao_encerrar_execucao(self, _dados: dict) -> None:
        self.botao_iniciar.setEnabled(True)
        self.botao_parar.setEnabled(False)
        self._habilitar_botoes_reprocessar(True)

    def _ao_finalizar_thread(self) -> None:
        self.trabalhador_atual = None

    def _tratar_erro_fatal(self, mensagem: str) -> None:
        QMessageBox.critical(self, "Erro na automacao", mensagem)

    def _renderizar_pagina_logs(self) -> None:
        self.tabela_logs.setRowCount(0)

        for linha, registro in enumerate(self._obter_registros_pagina_logs()):
            self.tabela_logs.insertRow(linha)
            self._setar_item_texto(
                linha,
                0,
                registro["id_linha"],
                cor=PALETA_CORES["texto_mutado"],
                fonte=self.fonte_mono,
            )
            self._setar_item_texto(
                linha,
                1,
                registro["cliente"],
                cor=(
                    PALETA_CORES["primaria"]
                    if registro["cliente"].lower() == "sistema"
                    else PALETA_CORES["texto_padrao"]
                ),
                destaque=registro["cliente"].lower() == "sistema",
            )
            self.tabela_logs.setCellWidget(
                linha,
                2,
                self._criar_widget_status_tabela(registro["status"]),
            )
            self._setar_item_texto(
                linha,
                3,
                registro["mensagem"],
                cor=PALETA_CORES["texto_padrao"],
                dica=registro["mensagem_original"],
            )
            self._setar_item_texto(
                linha,
                4,
                registro["horario"],
                cor=PALETA_CORES["texto_mutado"],
                fonte=self.fonte_mono,
            )

            if registro["pode_reprocessar"]:
                botao = QPushButton("Reprocessar")
                botao.setObjectName("botaoTabela")
                botao.setCursor(Qt.PointingHandCursor)
                botao.setMinimumHeight(34)
                botao.setMinimumWidth(LARGURA_COLUNA_LOG_ACAO - 22)
                botao.setEnabled(self.reprocessamento_habilitado)
                botao.clicked.connect(
                    partial(self.reprocessar_registro, registro["contexto"])
                )
                self.tabela_logs.setCellWidget(
                    linha,
                    5,
                    self._criar_widget_acao_tabela(botao),
                )
            else:
                self._setar_item_texto(
                    linha,
                    5,
                    "",
                    alinhamento=Qt.AlignRight | Qt.AlignVCenter,
                    cor=PALETA_CORES["texto_sutil"],
                )

            self.tabela_logs.setRowHeight(linha, ALTURA_LINHA_LOG)

        self._atualizar_controles_paginacao_logs()

    def _obter_registros_pagina_logs(self) -> list[dict]:
        if not self.registros_logs:
            return []

        inicio = self.indice_pagina_logs * self.linhas_por_pagina_logs
        fim = inicio + self.linhas_por_pagina_logs
        return self.registros_logs[inicio:fim]

    def _obter_total_paginas_logs(self) -> int:
        if not self.registros_logs:
            return 1
        return (
            len(self.registros_logs) + self.linhas_por_pagina_logs - 1
        ) // self.linhas_por_pagina_logs

    def _obter_ultima_pagina_logs(self) -> int:
        return self._obter_total_paginas_logs() - 1

    def _obter_chave_consolidacao_registro(
        self, dados: dict
    ) -> tuple[str, str, int, int] | None:
        cliente = str(dados.get("cliente", "-")).strip().lower()
        identificador = str(dados.get("identificador", "")).strip()

        if not identificador or cliente == "sistema" or identificador.lower() == "sistema":
            return None

        return (
            str(dados.get("id_linha", "-")).strip() or "-",
            identificador,
            int(dados.get("numero_pagina", 0) or 0),
            int(dados.get("numero_linha", 0) or 0),
        )

    def _localizar_indice_registro_existente(
        self, chave_consolidacao: tuple[str, str, int, int] | None
    ) -> int | None:
        if chave_consolidacao is None:
            return None

        for indice, registro in enumerate(self.registros_logs):
            if registro.get("chave_consolidacao") == chave_consolidacao:
                return indice

        return None

    def _sincronizar_totais_logs(self) -> None:
        self.total_logs = len(self.registros_logs)
        self.total_logs_reprocessaveis = sum(
            1 for registro in self.registros_logs if registro["pode_reprocessar"]
        )

    def _atualizar_controles_paginacao_logs(self) -> None:
        total_registros = len(self.registros_logs)
        total_paginas = self._obter_total_paginas_logs()
        self.indice_pagina_logs = min(
            self.indice_pagina_logs,
            self._obter_ultima_pagina_logs(),
        )

        if total_registros == 0:
            self.rotulo_contagem_logs.setText("Mostrando 0-0 de 0 registros")
        else:
            inicio = (self.indice_pagina_logs * self.linhas_por_pagina_logs) + 1
            fim = min(
                inicio + self.linhas_por_pagina_logs - 1,
                total_registros,
            )
            self.rotulo_contagem_logs.setText(
                f"Mostrando {inicio}-{fim} de {total_registros} registros"
            )

        self.rotulo_pagina_logs.setText(
            f"Pagina {self.indice_pagina_logs + 1} de {total_paginas}"
        )
        mostrar_navegacao = total_paginas > 1
        self.botao_pagina_anterior_logs.setVisible(mostrar_navegacao)
        self.botao_pagina_seguinte_logs.setVisible(mostrar_navegacao)
        self.rotulo_pagina_logs.setVisible(mostrar_navegacao)
        self.botao_pagina_anterior_logs.setEnabled(self.indice_pagina_logs > 0)
        self.botao_pagina_seguinte_logs.setEnabled(
            self.indice_pagina_logs < self._obter_ultima_pagina_logs()
        )

    def _ir_para_pagina_logs_anterior(self) -> None:
        if self.indice_pagina_logs <= 0:
            return
        self.indice_pagina_logs -= 1
        self._renderizar_pagina_logs()

    def _ir_para_pagina_logs_seguinte(self) -> None:
        if self.indice_pagina_logs >= self._obter_ultima_pagina_logs():
            return
        self.indice_pagina_logs += 1
        self._renderizar_pagina_logs()

    def _ajustar_altura_tabela_logs(self) -> None:
        altura_tabela = (
            ALTURA_CABECALHO_TABELA_LOG
            + (self.linhas_por_pagina_logs * ALTURA_LINHA_LOG)
            + 4
        )
        self.tabela_logs.setFixedHeight(altura_tabela)
        self.container_tabela_logs.setMinimumHeight(altura_tabela + 16)
        self.container_tabela_logs.setMaximumHeight(altura_tabela + 16)

    def _aplicar_estilo_global(self) -> None:
        self.setStyleSheet(
            f"""
            QMainWindow, QWidget#widgetCentral, QScrollArea#scrollPrincipal {{
                background: {PALETA_CORES['fundo']};
                color: {PALETA_CORES['texto_padrao']};
            }}
            QScrollArea#scrollPrincipal {{
                border: none;
            }}
            QScrollArea#scrollPrincipal > QWidget > QWidget {{
                background: transparent;
            }}
            QFrame#cabecalhoPainel {{
                background: {PALETA_CORES['branco']};
                border: 1px solid {PALETA_CORES['borda']};
                border-radius: 24px;
            }}
            QFrame#cabecalhoStatus {{
                background: {PALETA_CORES['superficie_secundaria']};
                border: 1px solid {PALETA_CORES['borda_forte']};
                border-radius: 20px;
            }}
            QFrame#rodapePainel {{
                background: transparent;
                border: none;
                border-top: 1px solid {PALETA_CORES['borda_forte']};
            }}
            QLabel#etiquetaTopo {{
                background: #EAF2FC;
                color: {PALETA_CORES['primaria']};
                border-radius: 11px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.4px;
            }}
            QLabel#logoFallback {{
                color: {PALETA_CORES['primaria']};
                font-size: 24px;
                font-weight: 800;
            }}
            QLabel#rodapeTitulo {{
                color: {PALETA_CORES['texto_padrao']};
                font-size: 12px;
                font-weight: 800;
            }}
            QLabel#rodapeTexto {{
                color: {PALETA_CORES['texto_mutado']};
                font-size: 12px;
            }}
            QLabel#rotuloPercentual {{
                color: {PALETA_CORES['primaria']};
                font-size: 28px;
                font-weight: 800;
            }}
            QFrame#cartaoPadrao,
            QFrame#cartaoEstatistica,
            QFrame#resumoLogCard,
            QFrame#containerTabelaLogs {{
                background: {PALETA_CORES['branco']};
                border: 1px solid {PALETA_CORES['borda']};
                border-radius: 20px;
            }}
            QPushButton#botaoPrimario {{
                background: {PALETA_CORES['primaria']};
                color: white;
                border: none;
                border-radius: 14px;
                padding: 13px 20px;
                font-weight: 700;
                min-width: 168px;
            }}
            QPushButton#botaoPrimario:hover {{
                background: #1A3970;
            }}
            QPushButton#botaoPrimario:pressed {{
                background: #15315E;
            }}
            QPushButton#botaoPerigo {{
                background: white;
                color: {PALETA_CORES['perigo']};
                border: 1px solid #E4BDB8;
                border-radius: 14px;
                padding: 13px 20px;
                font-weight: 700;
                min-width: 168px;
            }}
            QPushButton#botaoPerigo:hover {{
                background: #FFF7F5;
            }}
            QPushButton#botaoSecundario {{
                background: white;
                color: {PALETA_CORES['primaria']};
                border: 1px solid {PALETA_CORES['borda_forte']};
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: 700;
                min-width: 148px;
            }}
            QPushButton#botaoSecundario:hover {{
                background: #F8FBFF;
            }}
            QPushButton#botaoPaginacao {{
                background: white;
                color: {PALETA_CORES['primaria']};
                border: 1px solid {PALETA_CORES['borda_forte']};
                border-radius: 10px;
                min-width: 38px;
                max-width: 38px;
                min-height: 34px;
                max-height: 34px;
                font-weight: 800;
            }}
            QPushButton#botaoPaginacao:hover {{
                background: #F8FBFF;
            }}
            QLabel#rotuloPaginacaoLogs {{
                color: {PALETA_CORES['texto_mutado']};
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#botaoTabela {{
                background: #EFF5FD;
                color: {PALETA_CORES['primaria']};
                border: 1px solid {PALETA_CORES['borda_forte']};
                border-radius: 10px;
                padding: 8px 12px;
                font-weight: 700;
            }}
            QPushButton#botaoTabela:hover {{
                background: #E4EEFA;
            }}
            QPushButton#botaoTabela:disabled {{
                background: #F1F5F9;
                color: #94A3B8;
                border-color: #E2E8F0;
            }}
            QPushButton:disabled {{
                background: #E2E8F0;
                color: #94A3B8;
                border-color: #E2E8F0;
            }}
            QTableWidget#tabelaLogs {{
                background: white;
                border: none;
                outline: none;
                gridline-color: transparent;
                color: {PALETA_CORES['texto_padrao']};
            }}
            QTableWidget#tabelaLogs::item {{
                border-bottom: 1px solid #E6EDF5;
                padding: 6px 8px;
            }}
            QTableWidget#tabelaLogs::item:selected {{
                background: #EEF4FB;
                color: {PALETA_CORES['texto_padrao']};
            }}
            QHeaderView::section {{
                background: #F6F9FC;
                color: #52627A;
                border: none;
                border-bottom: 1px solid {PALETA_CORES['borda']};
                padding: 12px 14px;
                font-size: 12px;
                font-weight: 700;
            }}
            QProgressBar#barraProgresso {{
                border: none;
                border-radius: 7px;
                background: #E2E8F0;
            }}
            QProgressBar#barraProgresso::chunk {{
                border-radius: 7px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PALETA_CORES['primaria']}, stop:1 {PALETA_CORES['secundaria']});
            }}
            QScrollBar:vertical {{
                background: #EEF3F8;
                width: 14px;
                margin: 6px 2px 6px 2px;
                border: 1px solid #D9E4EF;
                border-radius: 7px;
            }}
            QScrollBar::handle:vertical {{
                background: #8FA6BE;
                border: 1px solid #7D95AE;
                border-radius: 6px;
                min-height: 42px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #6F87A2;
                border-color: #617996;
            }}
            QScrollBar::handle:vertical:pressed {{
                background: #5E7690;
                border-color: #516880;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
                border: none;
                height: 0px;
            }}
            """
        )

    def _aplicar_sombra(
        self,
        widget: QWidget,
        blur: int = 32,
        deslocamento_y: int = 8,
    ) -> None:
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(blur)
        sombra.setOffset(0, deslocamento_y)
        sombra.setColor(QColor(15, 23, 42, 24))
        widget.setGraphicsEffect(sombra)

    def _obter_logo_empresa(self) -> QPixmap | None:
        caminho_logo = resolver_caminho_recurso("public", "logo.png")
        if not caminho_logo.exists():
            return None

        pixmap = QPixmap(str(caminho_logo))
        if pixmap.isNull():
            return None
        return pixmap

    @staticmethod
    def _normalizar_mensagem_log(mensagem: str) -> str:
        return " ".join(mensagem.split())

    @staticmethod
    def _resumir_texto(texto: str, limite: int) -> str:
        if len(texto) <= limite:
            return texto
        return f"{texto[: limite - 3].rstrip()}..."

    @staticmethod
    def _formatar_inteiro(valor: int) -> str:
        return f"{valor:,}".replace(",", ".")
