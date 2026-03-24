@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "APP_NAME=RPA-Tabela-cliente"
set "DIST_DIR=dist\%APP_NAME%"
set "EXE_NAME=%APP_NAME%.exe"
set "INSTALLER_SCRIPT=installer\%APP_NAME%.iss"
set "INSTALLER_DIR=dist\instalador"
set "INSTALLER_NAME=%APP_NAME%-Setup.exe"

echo ============================================
echo   Build - Painel de Automacao RPA
echo ============================================
echo.

taskkill /IM %EXE_NAME% /F /T >nul 2>&1
ping 127.0.0.1 -n 2 >nul

if exist build (
    rmdir /S /Q build
    echo   build\ removido para rebuild limpo
)

if exist "%DIST_DIR%" (
    rmdir /S /Q "%DIST_DIR%"
    echo   %DIST_DIR%\ removido para rebuild limpo
)

if exist "%INSTALLER_DIR%" (
    rmdir /S /Q "%INSTALLER_DIR%"
    echo   %INSTALLER_DIR%\ removido para rebuild limpo
)

echo.
py -3.12 -m PyInstaller build.spec --clean --noconfirm

if %ERRORLEVEL% EQU 0 (
    if exist .env (
        copy /Y .env "%DIST_DIR%\.env" >nul
        echo   .env copiado para %DIST_DIR%\
    )

    call :resolver_iscc
    if not defined ISCC_EXE (
        call :instalar_inno_setup
        call :resolver_iscc
    )

    if defined ISCC_EXE (
        echo   Gerando instalador com Inno Setup...
        "!ISCC_EXE!" "%INSTALLER_SCRIPT%"
        if errorlevel 1 (
            echo   Falha ao gerar o instalador.
        ) else (
            echo   Instalador em: %INSTALLER_DIR%\%INSTALLER_NAME%
        )
    ) else (
        echo   Inno Setup nao encontrado. Instalador nao gerado.
    )

    echo.
    echo ============================================
    echo   Build concluido com sucesso!
    echo   Executavel em: %DIST_DIR%\%EXE_NAME%
    echo ============================================
) else (
    echo.
    echo ============================================
    echo   ERRO no build. Verifique os logs acima.
    echo ============================================
)

endlocal
if /I "%~1"=="--no-pause" goto :eof
pause
goto :eof

:resolver_iscc
set "ISCC_EXE="
for %%I in ("%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%ProgramFiles%\Inno Setup 6\ISCC.exe") do (
    if exist %%~I set "ISCC_EXE=%%~I"
)
if not defined ISCC_EXE (
    for /f "delims=" %%I in ('where ISCC 2^>nul') do (
        if not defined ISCC_EXE set "ISCC_EXE=%%I"
    )
)
exit /b 0

:instalar_inno_setup
where winget >nul 2>&1
if errorlevel 1 exit /b 0
echo   Inno Setup nao encontrado. Instalando via winget...
winget install --id JRSoftware.InnoSetup --exact --silent --accept-package-agreements --accept-source-agreements
exit /b 0
