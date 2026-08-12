<#
.SYNOPSIS
  Standalone o'rnatuvchi uchun PostgreSQL 16'ning o'rnatuvchisiz (binaries-only) Windows
  arxivini yuklab, faqat runtime uchun kerakli qismlarni (bin/lib/share — pgAdmin,
  StackBuilder, doc, include kabi ~200MB keraksiz og'irlikni tashlab) vendor/pgsql'ga
  joylashtiradi.

.NOTES
  Manba: EDB "Download PostgreSQL Binaries" sahifasi (www.enterprisedb.com/download-postgresql-binaries).
  Fayl ID vaqti-vaqti bilan yangi patch versiyaga almashishi mumkin — agar yuklab olish
  muvaffaqiyatsiz tugasa, sahifadan yangi havolani qo'lda tekshiring.
#>

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$VendorDir = Join-Path $RepoRoot "desktop\src-tauri\vendor\pgsql"
$DownloadUrl = "https://sbp.enterprisedb.com/getfile.jsp?fileid=1260308"  # PostgreSQL 16.14, Windows x86-64 binaries

if (Test-Path $VendorDir) {
    Write-Host "vendor/pgsql allaqachon mavjud — qayta yuklab olish uchun avval o'chiring: $VendorDir"
    exit 0
}

$Scratch = Join-Path $env:TEMP "kadr-vendor-pgsql"
New-Item -ItemType Directory -Force -Path $Scratch | Out-Null
$ZipPath = Join-Path $Scratch "pg16-binaries.zip"

Write-Host "PostgreSQL 16 binaries yuklab olinmoqda (~300MB)..."
Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipPath

Write-Host "Arxivdan chiqarilmoqda..."
$ExtractDir = Join-Path $Scratch "extracted"
Expand-Archive -Path $ZipPath -DestinationPath $ExtractDir -Force

New-Item -ItemType Directory -Force -Path $VendorDir | Out-Null
foreach ($sub in @("bin", "lib", "share")) {
    Copy-Item -Recurse -Force (Join-Path $ExtractDir "pgsql\$sub") (Join-Path $VendorDir $sub)
}

Remove-Item -Recurse -Force $Scratch

$SizeMB = [math]::Round((Get-ChildItem -Recurse $VendorDir | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "Tayyor: $VendorDir ($SizeMB MB)"
