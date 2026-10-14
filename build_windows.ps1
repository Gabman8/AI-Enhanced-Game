$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$bootstrapPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $bootstrapPython)) {
    throw "Project Python not found at $bootstrapPython. Create the environment first."
}
$buildPython = Join-Path $projectRoot '.buildvenv\Scripts\python.exe'

Push-Location $projectRoot
try {
    if (-not (Test-Path -LiteralPath $buildPython)) {
        & $bootstrapPython -m venv '.buildvenv'
        if ($LASTEXITCODE -ne 0) { throw 'Creating the isolated build environment failed.' }
    }

    & $buildPython -X utf8 -m pip install 'pygame==2.5.2' pyinstaller
    if ($LASTEXITCODE -ne 0) { throw 'Installing build dependencies failed.' }

    & $buildPython -m PyInstaller --noconfirm --clean --windowed --onedir `
        --name Comando `
        --add-data 'game\backgrounds;backgrounds' `
        --add-data 'game\images;images' `
        --add-data 'game\music;music' `
        --hidden-import AI.LLM.dialoge_generator `
        --distpath 'steam_upload\windows' `
        --workpath 'build\pyinstaller' `
        'game\main.py'
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }

    $exePath = Join-Path $projectRoot 'steam_upload\windows\Comando\Comando.exe'
    $smokeInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $smokeInfo.FileName = $exePath
    $smokeInfo.Arguments = '--smoke-test'
    $smokeInfo.WorkingDirectory = Split-Path -Parent $exePath
    $smokeInfo.UseShellExecute = $false
    $smokeInfo.Environment['SDL_VIDEODRIVER'] = 'dummy'
    $smokeInfo.Environment['SDL_AUDIODRIVER'] = 'dummy'
    $smokeProcess = [System.Diagnostics.Process]::Start($smokeInfo)
    if (-not $smokeProcess.WaitForExit(30000)) {
        Stop-Process -Id $smokeProcess.Id -Force -ErrorAction SilentlyContinue
        $smokeProcess.WaitForExit()
        throw 'The packaged game did not finish its bounded smoke test; it was stopped.'
    }
    if ($smokeProcess.ExitCode -ne 0) {
        throw "Packaged game smoke test failed with exit code $($smokeProcess.ExitCode)."
    }

    @'
COMANDO Windows build

Launch Comando.exe. Press F10 to exit at any time, including during gameplay.
The game also closes from the pause menu.

This directory is the Windows game build for a Steam depot. Create or configure
the Steam app and depot in Steamworks, then upload this entire Comando folder
with SteamPipe. Keep Comando.exe as the launch executable.
'@ | Set-Content -Encoding UTF8 'steam_upload\windows\Comando\README.txt'
    Write-Host "Build ready and smoke-tested: $exePath"
}
finally {
    Pop-Location
}
