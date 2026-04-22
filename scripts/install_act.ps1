# install_act.ps1
Write-Host "[Antigravity] Downloading Nektos Act for Windows..."
$releaseUrl = "https://github.com/nektos/act/releases/latest/download/act_Windows_x86_64.zip"
$destZip = ".\act.zip"

Invoke-WebRequest -Uri $releaseUrl -OutFile $destZip
Write-Host "[Antigravity] Extracting..."
Expand-Archive -Path $destZip -DestinationPath ".\bin" -Force
Remove-Item $destZip

Write-Host "[Antigravity] Act installed to .\bin\act.exe"
Write-Host "NOTE: Docker Desktop must be running for act to function."
