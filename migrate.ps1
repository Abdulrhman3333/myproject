# Set UTF-8 encoding for console
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Navigate to project directory
Set-Location "C:\Users\Microsoft\Desktop\local_progs\tahfeed_professional_website_2\myproject"

# Run migrations
Write-Host "Applying migrations..." -ForegroundColor Cyan
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nMigrations applied successfully!" -ForegroundColor Green
    
    # Run setup calendar
    Write-Host "`nSetting up academic calendar..." -ForegroundColor Cyan
    python setup_calendar.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nSetup completed successfully!" -ForegroundColor Green
        Write-Host "`nYou can now run: python manage.py runserver" -ForegroundColor Yellow
    } else {
        Write-Host "`nError setting up calendar" -ForegroundColor Red
    }
} else {
    Write-Host "`nError applying migrations" -ForegroundColor Red
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
