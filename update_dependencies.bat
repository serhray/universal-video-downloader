@echo off
echo ========================================
echo  Universal Video Downloader - Update
echo ========================================
echo.

echo [1/4] Atualizando dependencias...
pip install --upgrade -r requirements.txt

echo.
echo [2/4] Verificando instalacao do yt-dlp...
python -c "import yt_dlp; print(f'yt-dlp version: {yt_dlp.version.__version__}')"

echo.
echo [3/4] Testando Flask...
python -c "import flask; print(f'Flask version: {flask.__version__}')"

echo.
echo [4/4] Criando diretorio de logs...
if not exist "logs" mkdir logs

echo.
echo ========================================
echo  Atualizacao concluida!
echo ========================================
echo.
echo IMPORTANTE: Defina a variavel de ambiente SECRET_KEY para producao:
echo set SECRET_KEY=sua_chave_secreta_aqui
echo.
echo Para testar as correcoes, execute: run_web.bat
echo.
pause
