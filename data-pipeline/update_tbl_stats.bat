@echo off
REM Tampa Bay Lightning Stats Auto-Update Script
REM Runs daily: Prospects -> NHL -> Combine/Upload

echo ======================================================================
echo Tampa Bay Lightning - Daily Stats Update
echo ======================================================================
echo Started: %date% %time%
echo.

REM Change to the project directory
cd /d "C:\Users\hfras\Desktop\TBL Project"

REM ── Step 1: Scrape fresh prospect data ────────────────────────────────────
echo Step 1: Scraping prospects (In the System)...
python prospects_scraper_windows.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Prospects scraper failed! Check prospects_page_source.html
    echo Update aborted at %date% %time% - prospects scraper failed >> update_log.txt
    pause
    exit /b 1
)
echo.

REM Wait between requests to be polite to the server
timeout /t 10 /nobreak > nul

REM ── Step 2: Scrape fresh NHL roster stats ─────────────────────────────────
echo Step 2: Scraping NHL roster stats...
python selenium_nhl_scraper_windows.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: NHL scraper failed! Check selenium_page_source.html
    echo Update aborted at %date% %time% - NHL scraper failed >> update_log.txt
    pause
    exit /b 1
)
echo.

REM Wait before uploading
timeout /t 5 /nobreak > nul

REM ── Step 3: Combine and upload to MongoDB ─────────────────────────────────
echo Step 3: Combining data and uploading to MongoDB...
python combine_tbl_data.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Combine/upload failed!
    echo Update aborted at %date% %time% - combine script failed >> update_log.txt
    pause
    exit /b 1
)
echo.

echo ======================================================================
echo Update completed: %date% %time%
echo ======================================================================

echo Update completed successfully at %date% %time% >> update_log.txt

pause
