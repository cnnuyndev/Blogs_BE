# PowerShell script to fix line endings for Docker
Write-Host "Fixing line endings for Docker compatibility..." -ForegroundColor Green

# Convert entrypoint.sh to Unix line endings
if (Test-Path "entrypoint.sh") {
  Write-Host "Converting entrypoint.sh to Unix line endings..." -ForegroundColor Yellow
  $content = Get-Content "entrypoint.sh" -Raw
  $content = $content -replace "`r`n", "`n"
  [System.IO.File]::WriteAllText("entrypoint.sh", $content, [System.Text.Encoding]::UTF8)
  Write-Host "✓ entrypoint.sh converted" -ForegroundColor Green
}

Write-Host "Line endings fixed! You can now build your Docker image." -ForegroundColor Green
