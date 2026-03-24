"""==[DOC-FILE]===============================================================
Arquivo : src/infraestrutura/debug_visual.py
Classe  : DebugVisualClique (class)
Pacote  : src.infraestrutura
Modulo  : Infraestrutura - Debug Visual de Cliques

Papel   : Destaca visualmente o elemento alvo antes de cada clique do Selenium,
          desenhando borda vermelha, fundo translucido e circulo animado de pulso
          no ponto exato da interacao. Ativado via DEBUG_VISUAL=true no .env.

Conecta com:
- config - flag DEBUG_VISUAL
- selenium.webdriver - execucao de JavaScript no navegador
- src.infraestrutura.acoes_navegador - chamado antes de cada clique

Fluxo geral:
1) Verifica se DEBUG_VISUAL esta ativo; se nao, retorna imediatamente.
2) Injeta CSS de animacao no documento (uma unica vez por pagina).
3) Aplica highlight no elemento (borda + fundo vermelho translucido).
4) Cria circulo animado de pulso na posicao central do elemento.
5) Loga no console e no registrador qual elemento sera clicado.
6) Aguarda brevemente e remove os artefatos visuais.

Estrutura interna:
Metodos principais:
- destacar_antes_do_clique(): fluxo completo de destaque visual.
- destacar_antes_da_digitacao(): destaque para campos de input.
[DOC-FILE-END]==============================================================="""

import logging
import time
from typing import Optional

from selenium.common.exceptions import JavascriptException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

import config

_CSS_ANIMACAO_PULSO = """
@keyframes rpaDebugPulso {
  0%   { transform: translate(-50%, -50%) scale(0.3); opacity: 1; }
  50%  { transform: translate(-50%, -50%) scale(1.5); opacity: 0.5; }
  100% { transform: translate(-50%, -50%) scale(2.0); opacity: 0; }
}
""".strip()

_JS_INJETAR_CSS = """
(function() {
    if (document.getElementById('rpa-debug-style')) return;
    var style = document.createElement('style');
    style.id = 'rpa-debug-style';
    style.textContent = arguments[0];
    document.head.appendChild(style);
})();
"""

_JS_DESTACAR_ELEMENTO = """
(function(el) {
    el.setAttribute('data-rpa-border-original', el.style.outline || '');
    el.setAttribute('data-rpa-bg-original', el.style.backgroundColor || '');
    el.setAttribute('data-rpa-transition-original', el.style.transition || '');
    el.style.transition = 'outline 0.15s ease, background-color 0.15s ease';
    el.style.outline = '4px solid #e74c3c';
    el.style.backgroundColor = 'rgba(255, 0, 0, 0.12)';
})(arguments[0]);
"""

_JS_CRIAR_MARCADOR_PULSO = """
(function(el) {
    var rect = el.getBoundingClientRect();
    var cx = rect.left + rect.width / 2 + window.scrollX;
    var cy = rect.top + rect.height / 2 + window.scrollY;

    var marker = document.createElement('div');
    marker.className = 'rpa-debug-marker';
    marker.style.cssText = [
        'position: absolute',
        'left: ' + cx + 'px',
        'top: ' + cy + 'px',
        'width: 30px',
        'height: 30px',
        'border-radius: 50%',
        'background: radial-gradient(circle, rgba(231,76,60,0.8) 0%, rgba(231,76,60,0) 70%)',
        'pointer-events: none',
        'z-index: 2147483647',
        'animation: rpaDebugPulso 0.6s ease-out forwards'
    ].join('; ');

    document.body.appendChild(marker);
    return marker.className;
})(arguments[0]);
"""

_JS_REMOVER_DESTAQUE = """
(function(el) {
    el.style.outline = el.getAttribute('data-rpa-border-original') || '';
    el.style.backgroundColor = el.getAttribute('data-rpa-bg-original') || '';
    el.style.transition = el.getAttribute('data-rpa-transition-original') || '';
    el.removeAttribute('data-rpa-border-original');
    el.removeAttribute('data-rpa-bg-original');
    el.removeAttribute('data-rpa-transition-original');
})(arguments[0]);
"""

_JS_REMOVER_MARCADORES = """
document.querySelectorAll('.rpa-debug-marker').forEach(function(m) { m.remove(); });
"""

_JS_DESCREVER_ELEMENTO = """
(function(el) {
    var tag = el.tagName.toLowerCase();
    var id = el.id ? '#' + el.id : '';
    var cls = el.className && typeof el.className === 'string'
        ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.')
        : '';
    var texto = (el.textContent || '').trim().substring(0, 40);
    if (texto.length > 0) texto = ' "' + texto + '"';
    return '<' + tag + id + cls + '>' + texto;
})(arguments[0]);
"""

_JS_DESTACAR_INPUT = """
(function(el) {
    el.setAttribute('data-rpa-border-original', el.style.outline || '');
    el.setAttribute('data-rpa-bg-original', el.style.backgroundColor || '');
    el.setAttribute('data-rpa-transition-original', el.style.transition || '');
    el.style.transition = 'outline 0.15s ease, background-color 0.15s ease';
    el.style.outline = '4px solid #e74c3c';
    el.style.backgroundColor = 'rgba(255, 0, 0, 0.12)';
})(arguments[0]);
"""

TEMPO_DESTAQUE_CLIQUE = 0.5
TEMPO_DESTAQUE_INPUT = 0.3


class DebugVisualClique:
    def __init__(
        self,
        navegador: WebDriver,
        registrador: logging.Logger,
    ) -> None:
        self.navegador = navegador
        self.registrador = registrador
        self._css_injetado = False

    @property
    def ativo(self) -> bool:
        return config.DEBUG_VISUAL

    def destacar_antes_do_clique(self, elemento: WebElement) -> None:
        if not self.ativo:
            return

        try:
            self._garantir_css_injetado()
            descricao = self._descrever_elemento(elemento)
            self.registrador.info("[DEBUG VISUAL] Clicando em: %s", descricao)

            self.navegador.execute_script(_JS_DESTACAR_ELEMENTO, elemento)
            self.navegador.execute_script(_JS_CRIAR_MARCADOR_PULSO, elemento)

            time.sleep(TEMPO_DESTAQUE_CLIQUE)

            self.navegador.execute_script(_JS_REMOVER_DESTAQUE, elemento)
            self.navegador.execute_script(_JS_REMOVER_MARCADORES)
        except (JavascriptException, WebDriverException):
            pass

    def destacar_antes_da_digitacao(
        self, elemento: WebElement, valor: str
    ) -> None:
        if not self.ativo:
            return

        try:
            self._garantir_css_injetado()
            descricao = self._descrever_elemento(elemento)
            valor_exibido = valor[:20] + "..." if len(valor) > 20 else valor
            self.registrador.info(
                '[DEBUG VISUAL] Digitando "%s" em: %s', valor_exibido, descricao
            )

            self.navegador.execute_script(_JS_DESTACAR_INPUT, elemento)
            time.sleep(TEMPO_DESTAQUE_INPUT)
        except (JavascriptException, WebDriverException):
            pass

    def remover_destaque(self, elemento: WebElement) -> None:
        if not self.ativo:
            return

        try:
            self.navegador.execute_script(_JS_REMOVER_DESTAQUE, elemento)
        except (JavascriptException, WebDriverException):
            pass

    def _garantir_css_injetado(self) -> None:
        if self._css_injetado:
            return
        try:
            self.navegador.execute_script(_JS_INJETAR_CSS, _CSS_ANIMACAO_PULSO)
            self._css_injetado = True
        except (JavascriptException, WebDriverException):
            pass

    def _descrever_elemento(self, elemento: WebElement) -> str:
        try:
            return self.navegador.execute_script(
                _JS_DESCREVER_ELEMENTO, elemento
            ) or "(elemento)"
        except (JavascriptException, WebDriverException):
            return "(elemento)"
