# ================== CONFIG ==================
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvActivate = "$ProjectRoot\.venv\Scripts\activate.ps1"

$RedisExe  = "$ProjectRoot\conf\redis\redis-server.exe"
$RedisConf = "$ProjectRoot\conf\redis\redis.conf"

$LogDir = "$ProjectRoot\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# ================== PROCESS TRACKING ==================
$Managed = @{}  # Dictionary to track child processes

# ================== FUNCTIONS ==================
function Start-ManagedProcess {
    param (
        [string]$Name,
        [string]$Command,
        [string]$LogFile,
        [string]$WindowStyle = "Minimized"
    )

    Write-Host "Starting $Name..."

    $proc = Start-Process powershell `
        -PassThru `
        -WindowStyle $WindowStyle `
        -ArgumentList "-Command", "& {
            . '$VenvActivate'
            while (`$true) {
                Write-Host '[$Name] running'
                try {
                    Invoke-Expression '$Command' 2>&1 | Tee-Object -FilePath '$LogFile' -Append
                }
                catch {
                    Write-Host '[$Name] crashed'
                }
                Write-Host '[$Name] restarting in 5s...'
                Start-Sleep 5
            }
        }"

    $Managed[$Name] = $proc
}

# Gracefully send Ctrl+C to child process
function Send-CtrlC($proc) {
    try {
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait("^{C}")
    } catch {
        # fallback if SendKeys fails
        Stop-Process -Id $proc.Id -Force
    }
}

# Shutdown all child processes
function Shutdown-All {
    Write-Host "`Graceful shutdown started..."

    foreach ($name in $Managed.Keys) {
        $proc = $Managed[$name]
        if ($proc -and !$proc.HasExited) {
            Write-Host "Stopping $name (PID $($proc.Id))"
            Send-CtrlC $proc
        }
    }

    # Give processes some time to exit gracefully
    Start-Sleep 5

    foreach ($name in $Managed.Keys) {
        $proc = $Managed[$name]
        if ($proc -and !$proc.HasExited) {
            Write-Host "Force stopping $name (PID $($proc.Id))"
            Stop-Process -Id $proc.Id -Force
        }
    }

    Write-Host "All services stopped"
    exit
}

# Register shutdown when main terminal exits
Register-EngineEvent PowerShell.Exiting -Action { Shutdown-All } | Out-Null
# Also catch Ctrl+C
$null = Register-EngineEvent ConsoleCancelEvent -Action { Shutdown-All }

# ================== MAIN ==================
Write-Host "Starting DroomRobot System..."
. $VenvActivate

# Redis
Start-ManagedProcess `
    -Name "Redis" `
    -Command "`"$RedisExe`" `"$RedisConf`"" `
    -LogFile "$LogDir\redis.log"

Start-Sleep 2

# Services
Start-ManagedProcess `
    -Name "Dialogflow" `
    -Command "run-dialogflow" `
    -LogFile "$LogDir\dialogflow.log"

Start-Sleep 2

Start-ManagedProcess `
    -Name "GPT" `
    -Command "run-gpt" `
    -LogFile "$LogDir\gpt.log"

Start-Sleep 2

# GUI (no auto-restart, minimized terminal)
Write-Host "Starting GUI..."
$guiProc = Start-Process powershell `
    -PassThru `
    -WindowStyle Minimized `
    -ArgumentList "-Command", "& {
        . '$VenvActivate'
        python -m droomrobot.droomrobot_gui
    }"

$Managed["GUI"] = $guiProc

Write-Host "All services started"
Write-Host "Close THIS window to stop everything"

# Keep main terminal alive
while ($true) { Start-Sleep 60 }
