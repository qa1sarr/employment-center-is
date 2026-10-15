# GitHub -> SQL Server auto-sync
# Every N seconds checks GitHub (main). If files in database/ changed,
# pulls them and re-creates the EmploymentCenter database from schema_mssql.sql.
# NOTE: the database is dropped and re-created, so local data changes are lost.

param(
    [string]$Server   = "BORIBEK-QAISAR\BORIBEK",
    [string]$Repo     = "C:\Users\Admin\Desktop\employment-center-is",
    [int]$Interval    = 20
)

$ErrorActionPreference = "Stop"

function Deploy-Database {
    Write-Host "[$(Get-Date -Format HH:mm:ss)] Re-creating database EmploymentCenter..." -ForegroundColor Yellow
    $drop = "IF DB_ID(N'EmploymentCenter') IS NOT NULL BEGIN ALTER DATABASE EmploymentCenter SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE EmploymentCenter; END"
    sqlcmd -S $Server -E -C -b -Q $drop
    if ($LASTEXITCODE -ne 0) { throw "Drop failed" }
    sqlcmd -S $Server -E -C -b -f 65001 -i "$Repo\database\schema_mssql.sql"
    if ($LASTEXITCODE -ne 0) { throw "schema_mssql.sql failed" }
    Write-Host "[$(Get-Date -Format HH:mm:ss)] Database updated from GitHub." -ForegroundColor Green
}

Set-Location $Repo
git checkout main | Out-Null
git pull origin main | Out-Null

Write-Host "Initial deploy..." -ForegroundColor Cyan
Deploy-Database

Write-Host "Watching GitHub every $Interval sec. Press Ctrl+C to stop." -ForegroundColor Cyan
while ($true) {
    Start-Sleep -Seconds $Interval
    try {
        git fetch origin main -q
        $local  = (git rev-parse HEAD).Trim()
        $remote = (git rev-parse origin/main).Trim()
        if ($local -ne $remote) {
            $changed = git diff --name-only $local $remote -- database/
            git pull origin main | Out-Null
            Write-Host "[$(Get-Date -Format HH:mm:ss)] New commit from GitHub: $remote" -ForegroundColor Cyan
            if ($changed) { Deploy-Database }
        }
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
}
