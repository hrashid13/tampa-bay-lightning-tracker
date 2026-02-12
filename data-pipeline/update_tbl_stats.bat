@echo off
REM Tampa Bay Lightning Stats Auto-Update Script
REM This runs daily to update player stats

echo ======================================================================
echo Tampa Bay Lightning - Daily Stats Update
echo ======================================================================
echo Started: %date% %time%
echo.

REM Change to the project directory
cd /d "C:\Users\hfras\Desktop\TBL Project"

REM Run the Selenium scraper to get fresh NHL stats
echo Step 1: Scraping fresh NHL stats...
python selenium_nhl_scraper_windows.py
echo.

REM Wait a moment
timeout /t 5 /nobreak > nul

REM Run the combine script to upload to MongoDB
echo Step 2: Combining and uploading to MongoDB...
python combine_tbl_data.py
echo.

echo ======================================================================
echo Update completed: %date% %time%
echo ======================================================================

REM Optional: Log the results
echo Update completed at %date% %time% >> update_log.txt

pause