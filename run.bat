@echo off
echo ====================================
echo   Stock Analyzer Indonesia
echo ====================================
echo.

:menu
echo Pilih opsi:
echo 1. Jalankan Web App (Streamlit)
echo 2. Jalankan CLI - Quote
echo 3. Jalankan CLI - Analisa Lengkap
echo 4. Jalankan CLI - List Saham
echo 5. Install Dependencies
echo 6. Test Basic
echo 7. Keluar
echo.
set /p choice="Masukkan pilihan (1-7): "

if "%choice%"=="1" goto web
if "%choice%"=="2" goto cli_quote
if "%choice%"=="3" goto cli_full
if "%choice%"=="4" goto cli_list
if "%choice%"=="5" goto install
if "%choice%"=="6" goto test
if "%choice%"=="7" goto end

echo Pilihan tidak valid!
goto menu

:web
echo.
echo Starting Streamlit Web App...
echo Buka browser di http://localhost:8501
echo.
streamlit run app.py
goto menu

:cli_quote
echo.
set /p symbol="Masukkan simbol saham (contoh: BBCA): "
python cli.py quote %symbol%
echo.
pause
goto menu

:cli_full
echo.
set /p symbol="Masukkan simbol saham (contoh: BBCA): "
python cli.py full %symbol%
echo.
pause
goto menu

:cli_list
echo.
python cli.py list-stocks
echo.
pause
goto menu

:install
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Done!
pause
goto menu

:test
echo.
python test_basic.py
echo.
pause
goto menu

:end
echo.
echo Terima kasih!
exit
