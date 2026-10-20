# build_portable.ps1 - builds the portable Windows version of GeoChem App.
# Result: dist\GeoChemApp-<version>-windows-portable.zip (Python included,
# runs without installation or internet). Run it with build_portable.bat.
# Needs internet once, to download the official embeddable Python
# (python.org) and the libraries (pypi.org).
# Part of GeoChem App (GPL-3.0).

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"      # much faster downloads
$Here = $PSScriptRoot                          # ...\geo-app\tools\portable
$Root = Split-Path -Parent (Split-Path -Parent $Here)
$PyVer = "3.12.10"                             # last 3.12 release with Windows installers

$m = Select-String -Path (Join-Path $Root "app.py") -Pattern 'APP_VERSION = "([^"]+)"'
$Version = $m.Matches[0].Groups[1].Value
$Dist = Join-Path $Root "dist"
$Name = "GeoChemApp-$Version-windows-portable"
$Out = Join-Path $Dist $Name
Write-Host "Building $Name"

New-Item -ItemType Directory -Force -Path $Dist | Out-Null
if (Test-Path $Out) { Remove-Item $Out -Recurse -Force }
New-Item -ItemType Directory -Path (Join-Path $Out "python"), (Join-Path $Out "app"), (Join-Path $Out "examples") | Out-Null

# 1. Official embeddable Python (a complete Python in one folder)
$zip = Join-Path $Dist "python-$PyVer-embed-amd64.zip"
if (-not (Test-Path $zip)) {
    Write-Host "[1/4] Downloading Python $PyVer ..."
    Invoke-WebRequest "https://www.python.org/ftp/python/$PyVer/python-$PyVer-embed-amd64.zip" -OutFile $zip
} else { Write-Host "[1/4] Python $PyVer already downloaded" }
Expand-Archive $zip -DestinationPath (Join-Path $Out "python")
# allow the libraries in Lib\site-packages to be found
$pth = Get-ChildItem (Join-Path $Out "python") -Filter "python*._pth" | Select-Object -First 1
$lines = Get-Content $pth.FullName | ForEach-Object { $_ -replace '^#\s*import site', 'import site' }
$lines += "Lib\site-packages"
Set-Content -Path $pth.FullName -Value $lines -Encoding ascii

# 2. Libraries (Windows 64-bit wheels for Python 3.12), installed by the
#    Python of this computer into the portable folder
Write-Host "[2/4] Installing libraries (streamlit, pandas, numpy, matplotlib, openpyxl) ..."
$HostPy = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $HostPy)) { $HostPy = "python" }
& $HostPy -m pip install --disable-pip-version-check --no-warn-script-location `
    --target (Join-Path $Out "python\Lib\site-packages") `
    --platform win_amd64 --python-version 3.12 --implementation cp --only-binary=:all: `
    -r (Join-Path $Root "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Installing the libraries failed (see the messages above)." }

# 3. The app, examples and start files
Write-Host "[3/4] Copying the app ..."
$appDir = Join-Path $Out "app"
foreach ($f in "app.py", "README.md", "LICENSE", "CHANGELOG.md", "CITATION.cff", "requirements.txt") {
    Copy-Item (Join-Path $Root $f) $appDir
}
foreach ($d in "geochem", "docs", ".streamlit") {
    Copy-Item (Join-Path $Root $d) $appDir -Recurse
}
Get-ChildItem $appDir -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Copy-Item (Join-Path $Root "examples\*") (Join-Path $Out "examples")
Copy-Item (Join-Path $Here "launcher.py") $Out
Copy-Item (Join-Path $Here "Start GeoChem App.bat") $Out
Copy-Item (Join-Path $Here "READ ME FIRST.txt") $Out

# quick self-test: can the portable Python import the libraries?
& (Join-Path $Out "python\python.exe") -c "import streamlit, pandas, numpy, matplotlib, openpyxl; print('Self-test OK: streamlit', streamlit.__version__)"
if ($LASTEXITCODE -ne 0) { throw "Self-test failed: the portable Python cannot import the libraries." }
Get-ChildItem $Out -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# 4. ZIP file to share
Write-Host "[4/4] Making the ZIP file (this takes a few minutes) ..."
$zipOut = Join-Path $Dist "$Name.zip"
if (Test-Path $zipOut) { Remove-Item $zipOut -Force }
Compress-Archive -Path $Out -DestinationPath $zipOut -CompressionLevel Optimal
$mb = [math]::Round((Get-Item $zipOut).Length / 1MB, 1)
Write-Host ""
Write-Host "Done: $zipOut ($mb MB)"
Write-Host "Share this ZIP file. Your friend extracts it and double-clicks 'Start GeoChem App.bat'."
