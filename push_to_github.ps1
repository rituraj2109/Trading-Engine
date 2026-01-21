# PowerShell script to push to GitHub

Write-Host "Step 1: Create the repository on GitHub first!" -ForegroundColor Yellow
Write-Host "Go to: https://github.com/new" -ForegroundColor Cyan
Write-Host "Repository name: Trading-Engine-Backend" -ForegroundColor Cyan
Write-Host "Make it Public, don't initialize with README" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter after you've created the repository..." -ForegroundColor Green
Read-Host

Write-Host "Removing old remote if exists..." -ForegroundColor Yellow
git remote remove origin 2>$null

Write-Host "Adding new remote..." -ForegroundColor Yellow
git remote add origin https://github.com/rituraj2109/Trading-Engine-Backend.git

Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host "Done! Your code is now on GitHub." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to Railway.app" -ForegroundColor White
Write-Host "2. Create a new project or select existing" -ForegroundColor White
Write-Host "3. Connect your GitHub repository: rituraj2109/Trading-Engine-Backend" -ForegroundColor White
Write-Host "4. Add environment variables (see RAILWAY_DEPLOY.md)" -ForegroundColor White
