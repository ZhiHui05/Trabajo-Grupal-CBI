param(
    [ValidateSet("up", "down", "clean", "status", "build")]
    [string]$Action = "up"
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root
$Network = "cbi-modbus-ics"
$NetworkSubnet = if ($env:NETWORK_SUBNET) { $env:NETWORK_SUBNET } else { "172.28.0.0/24" }
$Modules = @(
    "plc",
    "hmi",
    "capture",
    "attacker"
)

function Ensure-Network {
    docker network inspect $Network *> $null
    if ($LASTEXITCODE -ne 0) {
        docker network create --driver bridge --subnet $NetworkSubnet $Network
    }
}

function Invoke-Compose([string]$Module, [string[]]$Arguments) {
    $ComposeFile = Join-Path $Root (Join-Path $Module "compose.yml")
    docker compose -f $ComposeFile @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose failed for module '$Module'."
    }
}

function Wait-ForPlc {
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        $Health = docker inspect --format '{{.State.Health.Status}}' cbi-plc 2>$null
        if ($LASTEXITCODE -eq 0 -and $Health -eq "healthy") {
            return
        }
        Start-Sleep -Seconds 2
    }
    throw "PLC did not become healthy within 60 seconds."
}

switch ($Action) {
    "up" {
        Ensure-Network
        Invoke-Compose "plc" @("up", "-d", "--build")
        Wait-ForPlc
        foreach ($module in @("hmi", "capture", "attacker")) {
            Invoke-Compose $module @("up", "-d", "--build")
        }
    }
    "down" {
        foreach ($module in @("attacker", "capture", "hmi", "plc")) {
            Invoke-Compose $module @("down")
        }
    }
    "clean" {
        foreach ($module in @("attacker", "capture", "hmi", "plc")) {
            Invoke-Compose $module @("down", "--rmi", "local", "--volumes")
        }
        docker network inspect $Network *> $null
        if ($LASTEXITCODE -eq 0) {
            docker network rm $Network
        }
    }
    "status" {
        foreach ($module in $Modules) {
            Invoke-Compose $module @("ps")
        }
    }
    "build" {
        Ensure-Network
        foreach ($module in $Modules) {
            Invoke-Compose $module @("build")
        }
    }
}
