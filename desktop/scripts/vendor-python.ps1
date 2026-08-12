<#
.SYNOPSIS
  Standalone o'rnatuvchi uchun: python.org'ning rasmiy ko'chma (embeddable) Python
  arxivini tayyorlaydi — pip bootstrap, backend/requirements-lock.txt'dan bog'liqliklar
  o'rnatiladi, so'ng backend manba kodi (app/alembic/scripts) nusxalanadi va
  site-packages'ga .pth fayli orqali bog'lanadi.

.NOTES
  Versiya backend/.venv'da SINALGAN versiya bilan ANIQ mos bo'lishi shart — aks holda
  kompilyatsiya qilingan kengaytmalar (asyncpg, cryptography, pydantic-core, nh3,
  argon2-cffi, pandas/numpy, lxml) yuklanmaydi. Hozircha: Python 3.14.6.

  Ko'chma Python `._pth` fayli PYTHONPATH'ni ATAYLAB e'tiborsiz qoldiradi (izolatsiya
  xususiyati) — shu sabab backend kodi oddiy nusxalab qo'yish bilan emas, site-packages
  ichidagi .pth fayli orqali ulanadi (bu mexanizm site.py orqali ishlaydi, ._pth
  izolatsiyasidan mustaqil).
#>

$ErrorActionPreference = "Stop"

$PythonVersion = "3.14.6"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$VendorDir = Join-Path $RepoRoot "desktop\src-tauri\vendor\pyruntime"
$BackendVendorDir = Join-Path $RepoRoot "desktop\src-tauri\vendor\backend"
$LockFile = Join-Path $RepoRoot "backend\requirements-lock.txt"

if (Test-Path $VendorDir) {
    Write-Host "vendor/pyruntime allaqachon mavjud — qayta yuklab olish uchun avval o'chiring: $VendorDir"
    exit 0
}

$Scratch = Join-Path $env:TEMP "kadr-vendor-python"
New-Item -ItemType Directory -Force -Path $Scratch | Out-Null
$ZipPath = Join-Path $Scratch "python-embed.zip"

Write-Host "Python $PythonVersion (embeddable) yuklab olinmoqda..."
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip" -OutFile $ZipPath

New-Item -ItemType Directory -Force -Path $VendorDir | Out-Null
Expand-Archive -Path $ZipPath -DestinationPath $VendorDir -Force

# `import site` yoqiladi + site-packages sys.path'ga qo'shiladi (standart ._pth
# izolatsiya rejimida ikkalasi ham o'chirilgan bo'ladi)
$PthFile = Get-ChildItem $VendorDir -Filter "python3*._pth" | Select-Object -First 1
@"
python$($PythonVersion.Substring(0,1))$($PythonVersion.Split('.')[1]).zip
.
Lib\site-packages

import site
"@ | Set-Content -Path $PthFile.FullName -Encoding ASCII

Write-Host "pip bootstrap qilinmoqda..."
$GetPip = Join-Path $Scratch "get-pip.py"
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $GetPip
& (Join-Path $VendorDir "python.exe") $GetPip --no-warn-script-location

Write-Host "backend/requirements-lock.txt o'rnatilmoqda..."
$SitePackages = Join-Path $VendorDir "Lib\site-packages"
& (Join-Path $VendorDir "python.exe") -m pip install --target $SitePackages -r $LockFile

# pandas/numpy o'zlarining test to'plamlarini ham o'rnatadi (~40MB+, runtime'da hech
# qachon import qilinmaydi) — ba'zi test fayllarining chuqur ichma-ich yo'llari
# Windows'ning 260 belgili MAX_PATH chegarasidan oshib ketishi ham mumkin (haqiqatan
# ham shu muammoga duch kelindi). Shu sabab olib tashlanadi — ikkala muammoni ham
# (hajm va yo'l uzunligi) birdaniga hal qiladi.
Write-Host "Runtime'da kerak bo'lmagan test papkalari tozalanmoqda..."
Get-ChildItem -Path $SitePackages -Recurse -Directory -Filter "tests" -ErrorAction SilentlyContinue |
    ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
Get-ChildItem -Path $SitePackages -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    ForEach-Object { Remove-Item -Recurse -Force $_.FullName }

Write-Host "Backend manba kodi nusxalanmoqda..."
New-Item -ItemType Directory -Force -Path $BackendVendorDir | Out-Null
foreach ($item in @("app", "alembic", "alembic.ini", "scripts")) {
    Copy-Item -Recurse -Force (Join-Path $RepoRoot "backend\$item") $BackendVendorDir
}
Get-ChildItem -Recurse -Directory -Filter "__pycache__" $BackendVendorDir | Remove-Item -Recurse -Force

# Backend kodini site-packages'ga bog'lash — ._pth PYTHONPATH'ni e'tiborsiz qoldirgani
# uchun oddiy muhit o'zgaruvchisi orqali ulab bo'lmaydi (vendor-python.ps1 docstring'iga q.)
Set-Content -Path (Join-Path $VendorDir "Lib\site-packages\kadr_backend.pth") -Value $BackendVendorDir -Encoding ASCII

Remove-Item -Recurse -Force $Scratch

$SizeMB = [math]::Round((Get-ChildItem -Recurse $VendorDir, $BackendVendorDir | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "Tayyor: $VendorDir + $BackendVendorDir ($SizeMB MB)"
