<#
Uploads variables from a local .env file to the currently linked Railway project.

Usage:
1. Install Railway CLI and `railway login` (interactive).
2. From repo root run: `railway init` or `railway link` to link the project.
3. Run this script to push variables: `.
ailway_env_from_dotenv.ps1`

This script will NOT show values; it posts them to Railway variables securely.
#>

if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Error "Railway CLI not found. Install it first (npm i -g railway) and run 'railway login'."
    exit 1
}

$envFile = Join-Path -Path (Get-Location) -ChildPath ".env"
if (-not (Test-Path $envFile)) {
    Write-Error ".env file not found in current folder. Create it with your API keys first."
    exit 1
}

Write-Host "Uploading variables from $envFile to Railway..."

Get-Content $envFile | ForEach-Object {
    if ($_ -and -not $_.StartsWith('#')) {
        $split = $_ -split '=', 2
        if ($split.Count -eq 2) {
            $key = $split[0].Trim()
            $value = $split[1].Trim()
            if ($key -and $value) {
                Write-Host "Setting $key..."
                railway variables set $key $value | Out-Null
            }
        }
    }
}

Write-Host "Done. Verify variables in Railway dashboard or run 'railway variables'"
