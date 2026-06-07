@echo off
echo ========================================
echo   PUSH TO GITHUB - Stock Analyzer
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git belum terinstall!
    echo Download: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Navigate to project directory
cd /d D:\saham

REM Check if remote already exists
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo.
    echo [INFO] Belum ada remote repository.
    echo.
    echo ============================================
    echo   LANGKAH 1: Buat Repository di GitHub
    echo ============================================
    echo.
    echo 1. Buka browser: https://github.com/new
    echo 2. Repository name: stock-analyzer-indonesia
    echo 3. Pilih: Public
    echo 4. Klik "Create repository"
    echo 5. Copy URL repository (contoh:
    echo    https://github.com/USERNAME/stock-analyzer-indonesia.git)
    echo.
    set /p REPO_URL="Masukkan URL repository GitHub: "
    echo.
    git remote add origin %REPO_URL%
    echo [OK] Remote ditambahkan!
) else (
    echo [OK] Remote repository sudah ada.
)

REM Set branch to main
git branch -M main

REM Add all files
echo.
echo [INFO] Menambahkan file ke git...
git add .

REM Commit
echo.
echo [INFO] Committing...
git commit -m "Stock Analyzer Indonesia - Super Lengkap"

REM Push
echo.
echo [INFO] Pushing ke GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Push gagal! 
    echo Pastikan:
    echo 1. Repository sudah dibuat di GitHub
    echo 2. URL remote sudah benar
    echo 3. Sudah login GitHub (git config)
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS! Kode sudah di-push ke GitHub
echo ========================================
echo.
echo Langkah selanjutnya:
echo 1. Buka: https://share.streamlit.io
echo 2. Login dengan GitHub
echo 3. Klik "New app"
echo 4. Pilih repository: stock-analyzer-indonesia
echo 5. Main file: app.py
echo 6. Klik "Deploy!"
echo.
pause
