"""==[DOC-FILE]===============================================================
Arquivo : src/ui/componentes.py
Classe  : EtiquetaStatus, CartaoEstatistica
Pacote  : src.ui
Modulo  : UI - Componentes Visuais

Papel   : Reune widgets reutilizaveis do dashboard desktop, com foco em
          status visual e exibicao de indicadores numericos.

Conecta com:
- PySide6.QtWidgets - base dos componentes visuais
- src.ui.ui_main - janela que consome estes widgets

Fluxo geral:
1) Define a paleta visual central da interface.
2) Renderiza badges de status com cor semantica.
3) Renderiza cartoes de estatistica com hierarquia visual mais corporativa.

Estrutura interna:
Classes principais:
- EtiquetaStatus: badge arredondado para status do robo e da tabela.
- CartaoEstatistica: card reutilizavel para total, processados, sucessos e falhas.
[DOC-FILE-END]==============================================================="""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


PALETA_CORES = {
    "primaria": "#21478A",
    "secundaria": "#2B89D9",
    "fundo": "#F3F7FB",
    "sucesso": "#1F7A63",
    "perigo": "#B55045",
    "branco": "#FFFFFF",
    "texto_mutado": "#64748B",
    "texto_padrao": "#0F172A",
    "texto_sutil": "#94A3B8",
    "borda": "#D9E4F0",
    "borda_forte": "#C6D6E7",
    "superficie_secundaria": "#F7FAFD",
    "info": "#2B89D9",
}


class EtiquetaStatus(QLabel):
    MAPA_CORES_STATUS = {
        "Parado": ("#F8FAFC", "#475569", "#CBD5E1"),
        "Executando": ("#E8F1FF", "#1D4ED8", "#BFDBFE"),
        "Erro": ("#FEF2F2", "#B42318", "#FECACA"),
        "Sucesso": ("#ECFDF3", "#166534", "#BBF7D0"),
        "Processando": ("#EFF6FF", "#1E40AF", "#BFDBFE"),
    }

    def __init__(self, texto: str) -> None:
        super().__init__(texto)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(118)
        self.setFixedHeight(34)
        self.atualizar(texto)

    def atualizar(self, texto: str) -> None:
        cor_fundo, cor_fonte, cor_borda = self.MAPA_CORES_STATUS.get(
            texto,
            ("#F8FAFC", PALETA_CORES["texto_padrao"], PALETA_CORES["borda"]),
        )
        self.setText(texto)
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {cor_fundo};
                color: {cor_fonte};
                border: 1px solid {cor_borda};
                border-radius: 17px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 700;
            }}
            """
        )


class CartaoEstatistica(QFrame):
    def __init__(
        self,
        titulo: str,
        cor_destaque: str,
        valor_inicial: int | str = 0,
    ) -> None:
        super().__init__()
        self.setObjectName("cartaoEstatistica")
        self.setMinimumHeight(138)

        conteudo = QVBoxLayout(self)
        conteudo.setContentsMargins(18, 18, 18, 18)
        conteudo.setSpacing(12)

        topo = QHBoxLayout()
        topo.setSpacing(10)
        conteudo.addLayout(topo)

        marcador = QFrame()
        marcador.setFixedSize(10, 10)
        marcador.setStyleSheet(
            f"background: {cor_destaque}; border: none; border-radius: 5px;"
        )
        topo.addWidget(marcador)

        rotulo_titulo = QLabel(titulo)
        rotulo_titulo.setStyleSheet(
            f"""
            color: {PALETA_CORES['texto_mutado']};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.4px;
            """
        )
        topo.addWidget(rotulo_titulo)
        topo.addStretch(1)

        self.rotulo_valor = QLabel(self._formatar_valor(valor_inicial))
        self.rotulo_valor.setStyleSheet(
            f"""
            color: {PALETA_CORES['texto_padrao']};
            font-size: 30px;
            font-weight: 800;
            """
        )
        conteudo.addWidget(self.rotulo_valor)

        detalhe = QLabel("Atualizacao continua")
        detalhe.setStyleSheet(
            f"color: {PALETA_CORES['texto_sutil']}; font-size: 12px;"
        )
        conteudo.addWidget(detalhe)

    def atualizar_valor(self, valor: int) -> None:
        self.rotulo_valor.setText(self._formatar_valor(valor))

    @staticmethod
    def _formatar_valor(valor: int | str) -> str:
        if isinstance(valor, int):
            return f"{valor:,}".replace(",", ".")
        return str(valor)
