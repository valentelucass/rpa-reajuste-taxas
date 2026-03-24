# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec para o Painel de Automacao RPA.

Para gerar o executavel:
    py -3.12 -m PyInstaller build.spec

O resultado ficara em:
    dist/RPA-Tabela-cliente/RPA-Tabela-cliente.exe
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH)
APP_DIST_NAME = "RPA-Tabela-cliente"

# Selenium usa lazy imports em __getattr__, o PyInstaller nao detecta automaticamente
selenium_hiddenimports = collect_submodules("selenium")

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "public" / "app-icon.ico"), "public"),
        (str(ROOT / "public" / "app-icon.png"), "public"),
        (str(ROOT / "public" / "logo.png"), "public"),
        (str(ROOT / "public" / "fonts" / "Manrope-Variable.ttf"), "public/fonts"),
        (str(ROOT / "public" / "fonts" / "OFL-Manrope.txt"), "public/fonts"),
    ],
    hiddenimports=[
        *selenium_hiddenimports,
        "src",
        "src.aplicacao",
        "src.aplicacao.robo_reajuste_taxas",
        "src.infraestrutura",
        "src.infraestrutura.acoes_navegador",
        "src.infraestrutura.fabrica_navegador",
        "src.infraestrutura.arquivos_execucao",
        "src.infraestrutura.caminhos",
        "src.infraestrutura.registrador_execucao",
        "src.infraestrutura.debug_visual",
        "src.infraestrutura.rastreador_etapas",
        "src.monitoramento",
        "src.monitoramento.observador_execucao",
        "src.paginas",
        "src.paginas.pagina_login",
        "src.paginas.pagina_tabelas_cliente",
        "src.servicos",
        "src.servicos.gestor_ocorrencias",
        "src.servicos.processador_tabela_clientes",
        "src.servicos.reajustador_taxas",
        "src.ui",
        "src.ui.componentes",
        "src.ui.logger",
        "src.ui.rpa_worker",
        "src.ui.ui_main",
        "config",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "test"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_DIST_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=str(ROOT / "public" / "app-icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_DIST_NAME,
)
